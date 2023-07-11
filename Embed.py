import argparse
from EmbedRepo import EmbedRepo
from EmbedSitemap import EmbedSitemap
from env import DEEPLAKE_USERNAME, DEEPLAKE_DB

def main(args):
    if args.dir:
        embed = EmbedRepo(root_dir=args.dir, deeplake_username=args.username, deeplake_db=args.db)
    elif args.url:
        embed = EmbedSitemap(url=args.url, deeplake_username=args.username, deeplake_db=args.db)
    docs = embed.split()
    print(docs)
    print("saved: ", embed.save(docs))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Embed some text files.')
    parser.add_argument('-dir', type=str, required=False, help='The root directory of the text files to embed.')
    parser.add_argument('-url', type=str, required=False, help='The sitemap to embed.')
    parser.add_argument('-username', type=str, default=DEEPLAKE_USERNAME, help='The DeepLake username. Optional.')
    parser.add_argument('-db', type=str, default=DEEPLAKE_DB, help='The DeepLake database name. Optional.')
    
    args = parser.parse_args()

    main(args)
