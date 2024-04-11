# lupa(ESG)

Aplicação em Flask que coleta, trata e apresenta informações públicas fornecidas por empresas brasileiras sobre temas relacionados à pauta **ESG** (ou **ASG**, na sigla em português para Ambiental, Social e Governança).

O site está organizado em 4 canais:

O site foi implementado com a utilização dos frameworks Flask (Python) e Tailwind (CSS), além da biblioteca de componentes DaisyUI. Foi desenvolvido como trabalho de conclusão da certificação em Jornalismo de dados e automação do Master em Jornalismo de Dados, Automação e Data Storytelling do Insper.

O deploy foi feito no Render e o site está disponível [aqui](https://lupa-esg.onrender.com/).

## Estrutura do projeto

```
.
├── .gitignore
├── LICENSE
├── README.md
├── app.py
├── pictogramas.py
├── walk-the-talk
│   ├── main.py
│   ├── arquivos_cvm
│   ├── requirements.txt
│   └── modules
│       ├── ajusta_dados.py
│       ├── consulta_gpt.py
│       ├── download_cvm.py
│       ├── processa_pdf.py
│       ├── processa_xml.py
│       └── processa_zip.py
├── package-lock.json
├── package.json
├── postcss.config.js
├── requirements.txt
├── static
│   ├── css
│   └── images
├── tailwind.config.js
└── templates
```

- `app.py`: rotas e funções do Flask
- `walk-the-talk/`: funções para obtenção e tratamento de dados
- `static/css`: arquivos css compilados pelo Tailwind
- `static/images`: imagens utilizadas
- `templates/`: templates do frontend Flask

## Motivações

O projeto lupa(ESG) surgiu da dificuldade de encontrar informações estruturadas sobre práticas relacionadas à pauta ESG. Ainda que boa parte das empresas de capital aberto divulgue relatórios de sustentabilidade em suas páginas de RI (Relações Institucionais), não existe um padrão para essa divulgação: quase todos os relatórios são divulgados em longos e elaborados PDFs, o que dificulta a extração automatizada de dados e o acompanhamento objetivo por parte do público, da imprensa e dos stakeholders.

## Métodos e resultados

### De onde vêm os dados

Todos os dados apresentados aqui são recuperados do Portal Dados Abertos CVM, da CVM. Os dados são obtidos partir da busca e interpretação do "Formulário de Referência" (FRE) e parte deles é processada com a utilização do GPT-4, da OpenAI.

### O que é o "Formulário de Referência"?

Segundo a própria CVM, o FRE é "um documento eletrônico, de encaminhamento periódico e eventual, previsto no artigo 22, inciso II, da Resolução CVM nº 80/22, cujo encaminhamento à CVM deve se dar por meio do Sistema Empresas.NET. O Formulário de Referência de Companhias Abertas reúne todas as informações referentes ao emissor, como atividades, fatores de risco, administração, estrutura de capital, dados financeiros, comentários dos administradores sobre esses dados, valores mobiliários emitidos e operações com partes relacionadas."

### Como os dados são obtidos?

Os dados são obtidos por meio de um script desenvolvido em Python, que acessa periodicamente o Portal Dados Abertos CVM, baixa os arquivos em formato ZIP, descompacta-os, extraindo um arquivo XML onde são encontrados os dados e formulários em PDF enviados pelas empresas. Parte dos dados é utilizada de forma literal (a maioria numéricos) e parte é enviada ao GPT-4 por meio da API para interpretação.

- [Fonte dos dados](https://dados.cvm.gov.br/dataset/cia_aberta-doc-fre)

## Roadmap

O projeto **lupa(ESG)** é um trabalho em andamento e está em constante evolução. Além de melhorias na performance e execução do código, estas são algumas das ideias que estão no radar:

- Incorporar dados retroativos, possibilitando o acompanhamento histórico
- Desenvolver uma lógica de processamento dos relatórios integrados das empresas
- Aprimorar as análises e visualizações dos dados
- Implementar uma área com estatísticas gerais sobre os dados
- Desenvolver um sistema que permita a comparação entre empresas
- Incorporar raspadores de notícias relacionadas a cada empresa
- Implementar uma API para acesso aos dados

## Autor e contato

O projeto foi desenvolvido por Paulo Fehlauer.

Entre em contato pelos canais abaixo:

- [Portfolio web e audiovisual](https://fehla.xyz/)
- [LinkedIn](https://www.linkedin.com/in/paulo-fehlauer/)
- [Instagram](https://www.instagram.com/fehlauer/)

## Licença

O código deste projeto é distribuído sob uma licença MIT. Consulte o arquivo [LICENSE](LICENSE) para detalhes.
