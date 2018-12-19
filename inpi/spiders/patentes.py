# -*- coding: utf-8 -*-
import scrapy
import csv
import ipdb
from scrapy.exceptions import CloseSpider
from inpi.utils import format_nome_inventor
from inpi.utils import save_to_csv


class PatentesSpider(scrapy.Spider):
    name = 'patentes'
    base_url = 'https://gru.inpi.gov.br'
    start_urls = \
        ['https://gru.inpi.gov.br/pePI/servlet/LoginController?action=login']
    custom_settings = {
        'DOWNLOAD_TIMEOUT': 600,
    }

    def parse(self, response):
        # ipdb.set_trace()
        yield scrapy.Request(self.base_url+'/pePI/jsp/patentes/PatenteSearchBasico.jsp',callback=self.pre_consulta)

    def pre_consulta(self, response):
        # ipdb.set_trace()
        yield scrapy.Request(self.base_url+'/pePI/jsp/patentes/PatenteSearchAvancado.jsp', callback=self.consulta)

    def consulta(self, response):
        classificacoes_ipc = ['iC12N*', 'C12P*', 'C12Q*', 'A61K*', 'C12R*',
            'A61P*', 'G01N*', 'C07K*', 'C12M*', 'C07H*', 'A01H*', 'C12S*',
            'A01N*'
        ]
        formdata = {
            'NumPedido': '',
            'ListaNumeroPatente': '',
            'NumPrioridade': '',
            'CodigoPct': '',
            'DataDeposito1': '',
            'DataDeposito2': '',
            'DataPrioridade1': '',
            'DataPrioridade2': '',
            'DataDepositoPCT1': '',
            'DataDepositoPCT2': '',
            'DataPublicacaoPCT1': '',
            'DataPublicacaoPCT2': '',
            'ClassificacaoIPC': '',
            'CatchWordIPC': '',
            'Titulo': '',
            'Resumo': '',
            'NomeDepositante': '',
            'CpfCnpjDepositante': '',
            'NomeInventor': '',
            'RegisterPerPage': '20',
            'botao': ' pesquisar » ',
            'Action': 'SearchAvancado'
        }
        for ipc in classificacoes_ipc:
            formdata.update({'ClassificacaoIPC': ipc})
            yield scrapy.FormRequest.from_response(
                response,
                url='https://gru.inpi.gov.br/pePI/servlet/PatenteServletController',
                formdata=formdata,
                callback=self.lista
            )

    def lista(self, response):
        total_items = response.xpath("//div[@id='tituloEResumoContextGlobal']/font/b/text()").extract_first()
        print(total_items)
        # ipdb.set_trace()
        items = response.css('tbody.Context tr')
        for item in items:
            link = item.css('td font a.visitado::attr(href)').extract_first()
            yield scrapy.Request(self.base_url+link, callback=self.detalhes_patente)
        
        proxima_pagina = response.xpath(u"//a[contains(.,'Próxima')]/attribute::href").extract_first()
        # ipdb.set_trace()
        if proxima_pagina:
            yield scrapy.Request(self.base_url+proxima_pagina, callback=self.lista)

    def detalhes_patente(self, response):
        """
            Informações que deve estar na planilha
            - n do pedido
            - data do deposito
            - classificacao ipc
            - classificacao cpc
            - titulo
            - nome do depositante
            - nome do inventor
        """

        n_pedido = (response.xpath("//tr/td/font[contains(.,' do Pedido:')]/../following-sibling::td/font/text()").extract_first() or '').strip()
        data_deposito = (response.xpath("//tr/td/font[contains(.,'Data do Dep')]/../following-sibling::td/font/text()").extract_first() or '').strip()
        # data_publicacao = response.xpath("//tr/td/font[contains(.,'Data da Publica')]/../following-sibling::td/font/text()").extract_first().strip()
        # data_concessao = response.xpath("//tr/td/font[contains(.,'Data da Concess')]/../following-sibling::td/font/text()").extract_first().strip()
        # prioridade_unionista = None
        classificacao_ipc = (response.xpath("//tr/td/font[contains(.,'o IPC:')]/../following-sibling::td/font/a/text()").extract_first() or '').strip()
        classificacao_cpc = (response.xpath("//tr/td/font[contains(.,'o CPC:')]/../following-sibling::td/font/a/text()").extract_first() or '').strip()

            # with open('response.html', 'wb') as resposta:
            #     resposta.write(response.body)
            # ipdb.set_trace()
        titulo = (response.xpath("//tr/td/font[contains(.,'tulo:')]/../following-sibling::td/div/font/text()").extract_first() or '').strip()
        # resumo = response.xpath("//tr/td/font[contains(.,'Resumo:')]/../following-sibling::td/div/font/text()").extract_first().strip()
        nome_inventor = response.xpath("//tr/td/font[contains(.,'Nome do Inventor:')]/../following-sibling::td/font/text() | //tr/td/font[contains(.,'Nome do Inventor:')]/../following-sibling::td/font/font/a/text()").extract() or ''
        if nome_inventor:
            nome_inventor = format_nome_inventor(nome_inventor)
        nome_depositante = (response.xpath("//tr/td/font[contains(.,'Nome do Depositante:')]/../following-sibling::td/font/text()").extract_first() or '').strip()
        # print('{0}, {1}, {2}'.format(n_pedido, nome_inventor, nome_depositante))
        patente = {
            'n_pedido': n_pedido,
            'data_deposito': data_deposito,
            'classificacao_ipc': classificacao_ipc,
            'classificacao_cpc': classificacao_cpc,
            'titulo': titulo,
            'nome_inventor': nome_inventor,
            'nome_depositante': nome_depositante,
        }
        save_to_csv(patente)