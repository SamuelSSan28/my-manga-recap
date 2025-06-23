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

---

## Estrutura do projeto

```
/
├── main.py             # Script de entrada
├── modules/
│   ├── summarizer.py   # Sumarização de texto
│   ├── script_gen.py   # Geração de roteiro
│   ├── video_gen.py    # Montagem de vídeo
│   └── audio_gen.py    # Geração de áudio narrado
├── requirements.txt
├── README.md
```

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

  
 
