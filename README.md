# MangaRecap 🎥📚

## Descrição

O **MangaRecap** é uma ferramenta que gera vídeos curtos e roteiros para **resumir histórias de mangás**. Ideal para quem quer compartilhar resumos visuais e narrados das sagas. Utiliza inteligência artificial para criar conteúdo informativo e dinâmico.

---

## Funcionalidades

* 🎬 **Geração de vídeo curto**: automatiza a criação de vídeos estilo “shorts” contendo síntese da história.
* 📝 **Roteiros prontos**: produz scripts editáveis para narradores baseados nos pontos principais.
* 🔍 **Sumarização automática**: extrai os principais eventos, personagens e diálogos.
* 🖼️ **Processamento de imagens**: recebe imagens de cada capítulo, utiliza OCR para extrair os textos e gerar o resumo.
* 🛠️ **Exportação versátil**: permite exportar vídeo+roteiro em MP4, TXT ou JSON.

---

## Tecnologias utilizadas

* **Python** com bibliotecas como `transformers`, `moviepy` e `pyttsx3`
* Integração com APIs de IA para sumarização e síntese de voz
* **GitHub Actions** para automatizar testes e deploys

---

## Como começar

### 1. Clone este repositório

```bash
git clone https://github.com/SEU_USUARIO/my-manga-recap.git
cd my-manga-recap
```

### 2. Crie um ambiente virtual (opcional, mas recomendado)

```bash
python3 -m venv venv  
source venv/bin/activate  # Linux/macOS  
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Execute o script principal

```bash
python main.py --chapters_dir caminho/para/capitulos --output resumo.mp4
```

Parâmetros disponíveis:

* `--chapters_dir`: pasta contendo subdiretórios com as imagens de cada capítulo
* `--output`: nome do arquivo de vídeo de saída
* `--lang`: idioma da narração (ex: `pt`, `en`)

As configurações padrão desses argumentos estão em `modules/config.py`. Você
pode editar esse arquivo para alterar valores como modelo de IA, idioma ou
prompt de sumarização sem precisar passar tudo pela linha de comando.

---

## Estrutura do projeto

```
/
├── main.py             # Script de entrada
├── modules/
│   ├── summarizer.py   # Sumarização de texto
│   ├── script_gen.py   # Geração de roteiro
│   ├── video_gen.py    # Montagem de vídeo
│   ├── audio_gen.py    # Geração de áudio narrado
│   └── config.py       # Valores padrão de configuração
├── requirements.txt
└── README.md
```

## Fluxo de execução

1. `main.py` lê as configurações de `modules/config.py` e os argumentos da linha de comando.
2. As imagens são processadas por `modules/ocr.py` para extrair o texto de cada capítulo.
3. O texto extraído é resumido em `modules/summarizer.py` utilizando o prompt padrão.
4. `modules/script_gen.py` combina os resumos em um roteiro único.
5. Esse roteiro é transformado em narração em `modules/audio_gen.py`.
6. Por fim `modules/video_gen.py` sincroniza as imagens com o áudio e gera o vídeo final.

### Scraping de capítulos

Para baixar automaticamente capítulos de um site de mangá, utilize o script `scrape.py` em duas etapas:

1. **Coletar links** da página da série:

   ```bash
   python scrape.py fetch URL_DA_SERIE links.json
   ```

   Isso cria um `links.json` com todas as URLs dos capítulos encontrados.

2. **Baixar imagens** de cada capítulo listado no JSON:

   ```bash
   python scrape.py download links.json NomeDoManga
   ```

   As imagens serão salvas em `NomeDoManga/chapter-1`, `chapter-2`, etc. Um arquivo `scraper.log` registra horário e eventuais erros durante o processo.
   O scraper usa o Selenium em modo headless para renderizar a página e aguardar as imagens carregarem, o que ajuda a contornar bloqueios como o Cloudflare.


---

## Exemplos de uso

```bash
python main.py --chapters_dir manga/one_piece/chapters --output one_piece_short.mp4 --lang pt
```

Gera um vídeo com resumo narrado de *One Piece* a partir das imagens dos capítulos.

---

## Contribuindo

Contribuições são muito bem-vindas!
Siga estas etapas:

1. Abra um *issue* para discutir mudanças.
2. Faça um fork do repositório.
3. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`).
4. Faça suas alterações e adicione testes.
5. Envie um Pull Request.

---

  
 
