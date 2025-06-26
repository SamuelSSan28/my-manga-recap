"""Simple interactive menu for My Manga Recap."""

import sys
from typing import Optional

from modules.config import (
    DEFAULT_TEMP_DIR,
    DEFAULT_LANG,
    DEFAULT_VIDEO_WIDTH,
    DEFAULT_VIDEO_HEIGHT,
)
from main import main, parse_args
import argparse


def _run_main_interactive() -> None:
    print("\n=== Gerar Vídeo ===")
    chapters_dir = input("Diretório de capítulos [manga]: ").strip() or "manga"
    output = input("Arquivo de saída [video.mp4]: ").strip() or "video.mp4"
    lang = input(f"Idioma [{DEFAULT_LANG}]: ").strip() or DEFAULT_LANG
    temp = input(f"Diretório temporário [{DEFAULT_TEMP_DIR}]: ").strip() or DEFAULT_TEMP_DIR
    width = input(f"Largura do vídeo [{DEFAULT_VIDEO_WIDTH}]: ").strip() or str(DEFAULT_VIDEO_WIDTH)
    height = input(f"Altura do vídeo [{DEFAULT_VIDEO_HEIGHT}]: ").strip() or str(DEFAULT_VIDEO_HEIGHT)
    max_chapters = input("Processar até N capítulos (vazio = todos): ").strip()

    args = [
        "--chapters_dir", chapters_dir,
        "--output", output,
        "--lang", lang,
        "--temp", temp,
        "--width", width,
        "--height", height,
    ]
    if max_chapters:
        args.extend(["--max-chapters", max_chapters])

    sys.argv = ["main"] + args
    main()


def run_menu() -> None:
    while True:
        print("\n=== My Manga Recap ===")
        print("1. Gerar vídeo")
        print("2. Testar provedores de IA")
        print("3. Mostrar configuração atual")
        print("4. Sair")
        choice = input("Escolha uma opção: ").strip()

        if choice == "1":
            _run_main_interactive()
        elif choice == "2":
            import test_openai
            test_openai.test_ai_providers()
        elif choice == "3":
            from modules.config import print_config_status
            print_config_status()
        elif choice == "4":
            print("Até mais!")
            break
        else:
            print("Opção inválida!")


if __name__ == "__main__":
    run_menu()
