# 🎬 My Manga Recap

Sistema completo e adaptável para converter mangás em vídeos narrados com IA, com arquitetura modular e processamento otimizado.

## ✨ Funcionalidades

### 🧠 Sistema de IA Adaptável
- **OpenAI Provider**: GPT + TTS de qualidade premium (quando disponível)
- **Local Provider**: TTS local com pyttsx3 (sempre disponível)
- **Silent Provider**: Fallback com áudio de duração calculada (garantia de funcionamento)
- **Fallback automático**: Sistema inteligente que sempre encontra uma solução

### 🔍 Sistema de OCR Avançado
- **OpenAI Vision**: OCR com contexto usando GPT-4o (requer API key)
- **TrOCR**: Modelo da HuggingFace para maior precisão
- **Tesseract**: OCR local sempre disponível
- **Fallback inteligente**: Seleção automática do melhor provider

### 🖼️ Processamento de Imagem
- **Melhoria para OCR**: Contraste, nitidez, remoção de ruído
- **Auto-rotação**: Detecção e correção automática de rotação
- **Otimização para vídeo**: Redimensionamento e formatação
- **Técnicas específicas para mangá**: Remoção de fundo, threshold adaptativo

### 📝 Geração de Roteiros
- **Templates especializados**: Ação, diálogo, cenas gerais
- **Contexto inteligente**: Análise de cenas e personagens
- **Narrativa fluida**: Conexão entre cenas e capítulos
- **Múltiplos idiomas**: Suporte a português, inglês e japonês

### 🔊 Sistema de Áudio
- **Síntese de voz**: OpenAI TTS ou TTS local
- **Processamento avançado**: Silêncio, transições, metadados
- **Formato flexível**: MP3, WAV com configurações personalizáveis
- **Cache inteligente**: Evita reprocessamento desnecessário

### 🎥 Geração de Vídeo
- **Composição automática**: Imagens + áudio + transições
- **Títulos e créditos**: Geração automática de elementos visuais
- **Qualidade configurável**: HD, Full HD, 4K
- **Formato otimizado**: MP4 com codec H.264

### ⚡ Processamento em Lote
- **Múltiplos capítulos**: Processamento paralelo otimizado
- **Sistema de filas**: Workers configuráveis
- **Monitoramento**: Progresso em tempo real
- **Recuperação de erros**: Continuação automática

## 🛠️ Instalação Rápida

```bash
# Clone o repositório
git clone <repo_url>
cd my-manga-recap

# Crie um ambiente virtual
python3 -m venv venv
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
python3 -m src.main --chapters_dir "manga_folder" --output "test.mp4" --max-chapters 1 --force
```

### Menu Interativo
```bash
python3 -m src.interactive_cli
```

### Com OpenAI (Qualidade Premium)
```bash
# 1. Configure o arquivo .env
cp env.example .env
nano .env  # Adicione sua OPENAI_API_KEY

# 2. Execute com qualidade premium
python3 -m src.main --chapters_dir "manga_folder" --output "video.mp4"
```

### Processamento em Lote
```bash
# Processa múltiplos capítulos em paralelo
python3 -m src.main --chapters_dir "manga_folder" --output "chapter_%d.mp4"
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
OPENAI_VISION_MODEL=gpt-4o
MMR_LANG=pt
LOG_LEVEL=INFO
```

### Configurações Disponíveis

| Variável | Descrição | Padrão |
|----------|-----------|---------|
| `OPENAI_API_KEY` | Chave da API OpenAI | (vazio) |
| `OPENAI_MODEL` | Modelo GPT | `gpt-4o-mini` |
| `OPENAI_TTS_MODEL` | Modelo TTS | `tts-1` |
| `OPENAI_TTS_VOICE` | Voz do TTS | `alloy` |
| `OPENAI_VISION_MODEL` | Modelo de OCR Vision | `gpt-4o` |
| `MMR_LANG` | Idioma padrão das saídas | `pt` |
| `LOG_LEVEL` | Nível de logging | `INFO` |

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    My Manga Recap                          │
├─────────────────────────────────────────────────────────────┤
│  📁 src/                    # Código fonte principal      │
│  ├─ 🎯 main.py             # Entrypoint principal         │
│  ├─ 🖥️ interactive_cli.py  # Interface CLI interativa    │
│  ├─ ⚙️ config/             # Configurações e constantes  │
│  ├─ 🤖 ai_provider/        # Provedores de IA            │
│  │  ├─ base.py             # Interface base              │
│  │  └─ providers/          # OpenAI, Local, Silent      │
│  ├─ 🔍 ocr/                # Sistema de OCR              │
│  │  ├─ base.py             # Interface OCR               │
│  │  └─ providers/          # Tesseract, TrOCR           │
│  ├─ 🖼️ image_processor/    # Processamento de imagem     │
│  ├─ 📝 script_gen/         # Geração de roteiros         │
│  │  └─ templates/          # Templates especializados    │
│  ├─ 🔊 audio_gen/           # Síntese de áudio            │
│  ├─ 🎥 video_gen/          # Composição de vídeo         │
│  └─ 🛠️ utils/              # Utilitários e cache        │
├─────────────────────────────────────────────────────────────┤
│  📁 tests/                 # Testes automatizados        │
│  📁 docs/                  # Documentação                │
│  📁 examples/              # Exemplos de uso             │
│  📁 scripts/               # Scripts de utilidade        │
└─────────────────────────────────────────────────────────────┘
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
python3 -c "from src.config.settings import OPENAI_API_KEY; print('Configurado' if OPENAI_API_KEY else 'Não configurado')"

# Sistema usa automaticamente Local Provider
```

### Problema: "Sem arquivo .env"
```bash
# Copiar exemplo
cp env.example .env

# Sistema funciona sem .env (usa Local Provider)
```

### Problema: "Erro de dependências"
```bash
# Reinstalar dependências
pip install -r requirements.txt --upgrade

# Verificar versões
pip list | grep -E "(torch|opencv|moviepy)"
```

## 📊 Performance

| Operação | 1 Cap. (40 pgs) | Observações |
|----------|-----------------|-------------|
| OCR | ~10s | Independente do provedor |
| Script OpenAI | ~3s | Qualidade premium |
| Script Local | <1s | Instantâneo |
| Audio OpenAI | ~5s | Alta qualidade |
| Audio Local | ~1s | Qualidade sistema |
| Vídeo | ~3s | Processamento rápido |
| **Lote (10 cap.)** | **~2min** | **Processamento paralelo** |

## 🚀 Recursos Avançados

### 🔄 Sistema de Cache
- Cache inteligente para OCR, scripts e áudio
- TTL configurável para otimização
- Evita reprocessamento desnecessário

### 📊 Logging Estruturado
- Logs detalhados para debug
- Rotação automática de arquivos
- Níveis configuráveis (DEBUG, INFO, WARNING, ERROR)

### 🎨 Templates de Roteiro
- **Ação**: Para cenas de luta e movimento
- **Diálogo**: Para conversas e interações
- **Geral**: Para cenas neutras e transições

### ⚡ Processamento em Lote
- Workers configuráveis (padrão: 4)
- Sistema de filas para otimização
- Recuperação automática de erros

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch: `git checkout -b feature/nova-funcionalidade`
3. Implemente seguindo a arquitetura modular
4. Teste: `python3 -m pytest tests/`
5. Pull Request

## 📄 Licença

MIT License - veja o arquivo LICENSE para detalhes.

---

**🎬 Sistema que sempre funciona, com qualidade quando possível! 🎬**

*Arquitetura modular, processamento otimizado e interface intuitiva para transformar mangás em experiências audiovisuais envolventes.* 