# PoC: monitor de novos papers no arXiv

## Descrição

Construa uma rotina automatizada que irá monitorar, de forma inteligente, novos papers no arXiv nas áreas relacionadas a Engenharia de Software e Sistemas Inteligentes, que armazene metadados relevantes e produza notificações/relatórios dos itens detectados.

Sua solução deverá apresentar os seguintes elementos:
1. Executar periodicamente (ex.: a cada dia) a busca por novos papers no arXiv.
2. Esse processo deverá selecionar apenas papers que estejam relacionados a temática de "Software Engineering" e "Intelligent Systems".
3. Para cada paper selecionado, sua solução deverá extrair os metadados relevantes (arXiv ID, título, autores, resumo, data), e produzir uma pequena justificativa com nota para sua inclusão. A justificativa deve conter também uma nota de 0-5 indicando o fit do paper com a temática desejada.
4. A solução deverá exibir e/ou enviar um relatório com os papers detectados, incluindo os metadados e a justificativa de inclusão.

## Entregáveis

A entrega deverá ser feita por meio de um pull-request para o repositório original da solução, contendo:

1. Um fork deste repositório com código-fonte e README contendo as instruções de execução.  
    - As instruções devem permitir a execução da solução em ambiente unix-like (Linux, macOS) e Windows.
2. Relatório técnico curto (máx. 2 páginas) descrevendo a abordagem, decisões de implementação e limitações da solução.  
    - Esse relatório deverá apresentar uma figura/diagrama ilustrando a arquitetura da solução, descrevendo os principais componentes e fluxos de dados desde o input até o output.
3. Um vídeo curto (máx. 3 min) demonstrando a execução da solução.

## Observações

- Você está livre para utilizar o conjunto de ferramentas, bibliotecas, programas, frameworks e linguagens que considerar mais adequados para a solução.
- Você pode utilizar tanto soluções low-code (por exemplo: n8n, Make, Zapier, GitHub Actions para orquestração/agendamento ou plataformas de RPA leves) quanto soluções baseadas em código (por exemplo: Python/Node.js com consumo do feed do arXiv, bibliotecas de NLP/LLMs para sumarização/score, e containerização via Docker).
- Nosso intuito é avaliar sua capacidade de utilizar, combinar e integrar as ferramentas voltadas para construção de sistemas inteligentes de forma coesa, e eficiente.