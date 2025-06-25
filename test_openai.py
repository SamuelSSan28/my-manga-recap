#!/usr/bin/env python3
"""
Script de teste para verificar a integração com diferentes provedores de IA
"""
import os
import sys
from modules import AIManager, OpenAIProvider, LocalProvider, SilentProvider
from modules.config import print_config_status

def test_ai_providers():
    """Testa todos os provedores de IA disponíveis"""

    print("🧪 Teste de Provedores de IA")
    print("=" * 50)

    if AIManager is None:
        print("❌ Módulo ai_provider não encontrado. Teste não pode ser executado.")
        return False

    # Initialize AI manager
    ai_manager = AIManager()
    
    # Test data
    test_texts = [
        "O herói olha para o horizonte com determinação.",
        "Uma batalha épica está prestes a começar.",
        "O destino do mundo está em suas mãos.",
        "A jornada de mil milhas começa com um único passo."
    ]
    
    print("📝 Testando geração de roteiro...")
    script = ai_manager.generate_script(test_texts)
    
    if script:
        print("✅ Roteiro gerado com sucesso!")
        print(f"📄 Conteúdo ({len(script)} chars): {script[:200]}...")
        
        # Test audio generation
        print("\n🎤 Testando geração de áudio...")
        success = ai_manager.generate_audio(script, "test_audio.mp3")
        
        if success:
            print("✅ Áudio gerado com sucesso!")
            if os.path.exists("test_audio.mp3"):
                size = os.path.getsize("test_audio.mp3")
                print(f"🎵 Arquivo: {size} bytes")
                # Clean up
                os.remove("test_audio.mp3")
        else:
            print("❌ Falha na geração de áudio")
    else:
        print("❌ Falha na geração de roteiro")
    
    # Test individual providers
    print("\n🔍 Testando provedores individuais:")
    
    providers = []
    if OpenAIProvider is not None:
        providers.append(("OpenAI", OpenAIProvider()))
    if LocalProvider is not None:
        providers.append(("Local", LocalProvider()))
    if SilentProvider is not None:
        providers.append(("Silent", SilentProvider()))
    
    for name, provider in providers:
        print(f"\n{name} Provider:")
        available = provider.is_available()
        print(f"  Disponível: {'✅' if available else '❌'}")
        
        if available:
            # Test script generation
            test_script = provider.generate_script(test_texts[:2])  # Smaller test
            if test_script:
                print(f"  Script: ✅ ({len(test_script)} chars)")
            else:
                print(f"  Script: ❌")
    
    print("\n🎉 Teste concluído!")
    return True

def show_config():
    """Mostra configuração atual usando config centralizado"""
    print_config_status()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("Usage: python test_openai.py [--config]")
            print("  --config: Mostra configuração atual")
            print("\n💡 Para configurar OpenAI:")
            print("  1. Copie env.example para .env")
            print("  2. Edite .env e adicione sua OPENAI_API_KEY")
            sys.exit(0)
        elif sys.argv[1] == "--config":
            show_config()
            sys.exit(0)
    
    test_ai_providers() 
