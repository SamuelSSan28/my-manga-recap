# 🎬 My Manga Recap

Sistema completo e adaptável para converter mangás em vídeos narrados com IA.

## ✨ Funcionalidades

### 🧠 Sistema de IA Adaptável
- **OpenAI Provider**: GPT + TTS de qualidade premium (quando disponível)
- **Local Provider**: TTS local com pyttsx3 (sempre disponível)
- **Silent Provider**: Fallback com áudio de duração calculada (garantia de funcionamento)
- **Fallback automático**: Sistema inteligente que sempre encontra uma solução

### ⚙️ Configuração Simplificada com .env
- **Configuração centralizada**: Todas as configurações em um só lugar
- **Arquivo .env**: Configuração segura de API keys
- **Fallback inteligente**: Funciona sem configuração externa

## 🛠️ Instalação Rápida

```bash
# Clone o repositório
git clone <repo_url>
cd my-manga-recap

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# (Opcional) Configure OpenAI para qualidade premium
cp env.example .env
# Edite .env e adicione sua OPENAI_API_KEY
```

## 🚀 Uso Básico

### Teste Rápido (Sempre Funciona)
```bash
# Funciona sem qualquer configuração externa
python main.py --chapters_dir "manga_folder" --output "test.mp4" --max-chapters 1 --force
```

### Com OpenAI (Qualidade Premium)
```bash
# 1. Configure o arquivo .env
cp env.example .env
nano .env  # Adicione sua OPENAI_API_KEY

# 2. Execute com qualidade premium
python main.py --chapters_dir "manga_folder" --output "video.mp4"
```

### Verificar Sistema
```bash
# Verificar configuração atual
python test_openai.py --config

# Testar todos os provedores
python test_openai.py
```

## ⚙️ Configuração

### Arquivo .env
```bash
# Copie o exemplo
cp env.example .env

# Edite com suas configurações
OPENAI_API_KEY=sk-sua-chave-aqui
OPENAI_MODEL=gpt-4o-mini
OPENAI_TTS_MODEL=tts-1
OPENAI_TTS_VOICE=alloy
```

### Configurações Disponíveis

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `OPENAI_API_KEY` | Chave da API OpenAI | (vazio) |
| `OPENAI_MODEL` | Modelo GPT | `gpt-4o-mini` |
| `OPENAI_TTS_MODEL` | Modelo TTS | `tts-1` |
| `OPENAI_TTS_VOICE` | Voz do TTS | `alloy` |

### Vozes Disponíveis
- **alloy**: Voz neutra e clara
- **echo**: Voz masculina
- **fable**: Voz expressiva 
- **onyx**: Voz grave
- **nova**: Voz feminina
- **shimmer**: Voz suave

## 🤖 Sistema de Provedores

### 1. **OpenAI Provider** (Premium)
```bash
✅ Roteiros profissionais com GPT
✅ TTS de alta qualidade
✅ Múltiplas vozes naturais
⚠️  Requer API key e créditos
```

### 2. **Local Provider** (Sempre Disponível)
```bash
✅ Sempre funciona offline
✅ TTS com vozes do sistema
✅ Roteiros funcionais
⚠️  Qualidade dependente do sistema
```

### 3. **Silent Provider** (Garantia)
```bash
✅ Sempre funciona como último recurso
✅ Duração calculada baseada no texto
✅ Perfeito para testes
⚠️  Áudio silencioso
```

## 📊 Arquitetura do Sistema

```
┌─────────────────┐
│   main.py       │
└─────────┬───────┘
          │
┌─────────▼───────┐
│   modules/      │
│  ├─ config.py   │ ◄── Carrega .env
│  ├─ ai_provider │ ◄── Usa config
│  ├─ ocr.py      │
│  ├─ script_*    │
│  ├─ audio_gen   │
│  └─ video_gen   │
└─────────────────┘
```

## 🎯 Parâmetros CLI

| Parâmetro | Descrição | Padrão |
|-----------|-----------|---------|
| `--chapters_dir` | Diretório com capítulos | (obrigatório) |
| `--output` | Arquivo de vídeo de saída | (obrigatório) |
| `--max-chapters` | Limite de capítulos (teste) | Todos |
| `--force` | Ignorar checkpoints | False |
| `--temp` | Diretório temporário | `temp` |
| `--lang` | Idioma da narração | `pt` |
| `--width` | Largura do vídeo | 1280 |
| `--height` | Altura do vídeo | 720 |

## 🔧 Troubleshooting

### Problema: "OpenAI não funciona"
```bash
# Verificar configuração
python test_openai.py --config

# Sistema usa automaticamente Local Provider
```

### Problema: "Sem arquivo .env"
```bash
# Copiar exemplo
cp env.example .env

# Sistema funciona sem .env (usa Local Provider)
```

### Problema: "python-dotenv não encontrado"
```bash
# Instalar dependência
pip install python-dotenv

# Ou reinstalar todas
pip install -r requirements.txt
```

## 📁 Estrutura de Arquivos

```
my-manga-recap/
├── main.py              # Script principal
├── test_openai.py       # Teste de provedores
├── env.example          # Exemplo de configuração
├── .env                 # Suas configurações (não versionado)
├── requirements.txt     # Dependências
├── modules/
│   ├── __init__.py      # Exports do módulo
│   ├── config.py        # Configurações centralizadas
│   ├── ai_provider.py   # Sistema de IA
│   ├── ocr.py          # Extração de texto
│   ├── script_narrator.py # Geração de roteiros
│   ├── audio_gen.py    # Síntese de voz
│   └── video_gen.py    # Criação de vídeo
└── temp/               # Arquivos temporários
    ├── chapter_texts.json
    ├── narration_scripts.json
    └── narration.mp3
```

## 🎮 Exemplos Práticos

### Configuração Inicial
```bash
# 1. Copiar configuração
cp env.example .env

# 2. Editar com sua API key
echo "OPENAI_API_KEY=sk-sua-chave" > .env

# 3. Testar configuração
python test_openai.py --config
```

### Teste Básico
```bash
# Sempre funciona, sem configuração
python main.py --chapters_dir "manga" --output "test.mp4" --max-chapters 1
```

### Qualidade Premium
```bash
# Com OpenAI configurado
python main.py --chapters_dir "manga" --output "premium.mp4"
```

## 🔄 Fallback Inteligente

O sistema **nunca falha** graças ao fallback automático:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   OpenAI    │───▶│    Local    │───▶│   Silent    │
│  (Premium)  │    │   (Good)    │    │  (Always)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 📈 Performance

| Operação | 1 Cap. (40 pgs) | Observações |
|----------|-----------------|-------------|
| OCR | ~10s | Independente do provedor |
| Script OpenAI | ~3s | Qualidade premium |
| Script Local | <1s | Instantâneo |
| Audio OpenAI | ~5s | Alta qualidade |
| Audio Local | ~1s | Qualidade sistema |
| Vídeo | ~3s | Processamento rápido |

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/novo-provider`
3. Implemente seguindo a interface `AIProvider`
4. Teste: `python test_openai.py`
5. Pull Request

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

---

**🎬 Sistema que sempre funciona, com qualidade quando possível! 🎬** 