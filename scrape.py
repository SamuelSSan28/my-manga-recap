import argparse
import json

from modules.manga_scraper import fetch_chapter_links, download_chapters


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple manga scraper")
    subparsers = parser.add_subparsers(dest="cmd")

    fetch_p = subparsers.add_parser("fetch", help="Fetch chapter links (automatically sorted)")
    fetch_p.add_argument("series_url", help="URL of manga series page")
    fetch_p.add_argument("output_json", help="File to save chapter links and manga info")

    dl_p = subparsers.add_parser("download", help="Download chapters from JSON")
    dl_p.add_argument("links_json", help="JSON file with chapter links and manga info")
    dl_p.add_argument("--delay", type=float, default=1.0, help="Delay between image downloads")

    args = parser.parse_args()

    if args.cmd == "fetch":
        fetch_chapter_links(args.series_url, args.output_json)
    elif args.cmd == "download":
        download_chapters(args.links_json, delay=args.delay)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
