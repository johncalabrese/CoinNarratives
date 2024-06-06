import json
from flask import Flask,jsonify,render_template, send_from_directory
from flask_caching import Cache
from pycgapi import CoinGeckoAPI
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Assuming you have initialized your Flask app and cache
app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# Define the directory path where the images are stored
IMAGES_FOLDER = os.path.join(os.getcwd(), 'images')
app.config['IMAGES_FOLDER'] = IMAGES_FOLDER

# Initialize CoinGeckoAPI
coingecko_key = os.environ.get('COINGECKO_API_KEY')
cg = CoinGeckoAPI(coingecko_key, pro_api=False)

# Route to serve image files
@app.route('/images/<path:filename>')
def get_image(filename):
    return send_from_directory(app.config['IMAGES_FOLDER'], filename)

@app.route('/')
def index():
    return render_template('bubble_chart.html')

# API route to fetch data for all categories and the overall market
@app.route('/get_data')
@cache.cached(timeout=60)  # Cache data for 60 seconds
def get_data():
    # Define tokens for each category
    categories = {
        'rwa': ['artrade', 'chex-token', 'blocksquare', 'centrifuge', 'boson-protocol', 'creditcoin-2', 'canto', 'lcx', 'lto-network', 'mantra-dao', 'dusk-network', 'origintrail', 'linear', 'hifi-finance', 'pendle', 'goldfinch', 'ondo-finance', 'clearpool', 'opulous', 'maple', 'planet-token'],
        'defi': ['ferro', 'cream-2', 'bridge-oracle', 'dypius', 'harvest-finance', 'akropolis', 'seamless-protocol', 'just', 'airswap', 'barnbridge', 'helio-protocol-hay', 'dai', 'frax', 'olympus', 'crvusd', 'liquity-usd', 'nusd', 'chainlink', 'amber', 'alchemix', 'lever', 'jito-governance-token', 'auction', 'magic-internet-money', 'curve-dao-token', 'prisma-governance-token', 'bancor', '1inch', 'dforce-token', 'fuse-network-token', 'covalent', 'aurora-dao', 'prisma-mkusd', 'concentrated-voting-power', 'keep3rv1', 'compound-governance-token', 'coin98', 'gnosis', 'beefy-finance', 'aave', 'melon', 'balancer', 'alpaca-finance', 'gearbox', 'band-protocol', 'dia-data', '0x', 'chainflip', 'dydx', 'dydx-chain', 'velar', 'api3', 'chaingpt', 'convex-finance', 'amp-token', 'bonfida', 'badger-dao', 'vertex-protocol', 'alpha-finance', 'vvs-finance', 'benqi', 'dodo', 'ampleforth', 'nest', 'smardex', 'defi-yield-protocol', 'poolz-finance-2', 'staked-ether', 'lido-dao', 'frax-share', 'gains-network', 'cetus-protocol', 'havven', 'kyber-network-crystal', 'flamingo-finance', 'zkswap-finance', 'frontier-token', 'msol', 'force-protocol', 'yfii-finance', 'hashflow', 'oraichain-token', 'kava-lend', 'scallop-2', 'maker', 'venus', 'loopring', 'linear', 'hifi-finance', 'pendle', 'orca', 'seedify-fund', 'jupiter-exchange-solana', 'uniswap', 'wrapped-nxm', 'aevo-exchange', 'goldfinch', 'syncus', 'liquity', 'unlend-finance', 'pangolin', 'polkastarter', 'joe', 'yearn-finance', 'pancakeswap-token', 'serum', 'trava-finance', 'gmx', 'ribbon-finance', 'quickswap', 'wing-finance', 'tranchess', 'maple', 'the-graph', 'ethena', 'orion-protocol', 'saucerswap', 'wanchain', 'stp-network', 'wrapped-kava', 'stafi', 'subquery-network', 'raydium', 'thorchain', 'osmosis', 'rocket-pool', 'marlin', 'pyth-network', 'prosper', 'uma', 'terra-luna', 'truefi', 'woo-network', 'tokenfi', 'perpetual-protocol', 'stargate-finance', 'bella-protocol', 'reserve-rights-token', 'republic-protocol', 'sushi', 'spell-token', 'numeraire', 'tellor', 'unifi-protocol-dao'],
        'l2': ['matic-network', 'optimism', 'arbitrum', 'starknet', 'aevo-exchange', 'blockstack', 'mantle', 'immutable-x', 'manta-network', 'skale', 'metis-token', 'cyberconnect', 'loopring', 'wrapped-ether-mantle-bridge', 'boba-network', 'bitcoin-cats', 'cryptogpt-token', 'cartesi', 'satoshivm', 'zkspace', 'cocos-bcx', 'mintlayer'],
        'l1': ['bitcoin', 'ethereum', 'solana', 'binancecoin', 'the-open-network', 'near', 'tron', 'bitcoin-cash', 'cardano', 'sui', 'saga-2', 'avalanche-2', 'filecoin', 'fantom', 'aptos', 'injective-protocol', 'gala', 'cosmos', 'sei-network', 'mantra-dao', 'coredaoorg', 'tezos', 'hedera-hashgraph', 'chiliz', 'arweave', 'oasis-network', 'zetachain', 'flow', 'kaspa', 'algorand', 'monero', 'crypto-com-chain', 'ronin', 'vanar-chain', 'enjincoin', 'elrond-erd-2', 'chia', 'astar', 'flare-networks', 'ecash', 'klay-token', 'dusk-network', 'kava', 'lto-network', 'wax', 'moonriver', 'the-root-network', 'chromaway', 'moonbeam', 'aioz-network', 'kadena', 'amber', 'oraichain-token', 'radix', 'tomochain', 'nibiru', 'fio-protocol', 'canto', 'syscoin', 'gnosis', 'hive', 'alephium', 'aleph-zero', 'script-network', 'decred', 'coreum', 'tectum', 'qubic-network', 'fuse-network-token', 'oasys', 'concordium', 'spacemesh', 'qanplatform'],
        'meme': ['dogecoin', 'pepe', 'shiba-inu', 'dogwifcoin', 'book-of-meme', 'floki', 'memecoin-2', 'slerf', 'bonk', 'degen-base', 'wen-4', 'pups-ordinals', 'cat-in-a-dogs-world', 'myro', 'ponke', 'popcat', 'troll', 'arbdoge-ai', 'ansem-s-cat', 'catcoin-cash', 'peng', 'shark-cat', 'milady-meme-coin', 'based-brett', 'pepecoin-2', 'normie-2', 'turbo', 'jeo-boden', 'coq-inu', 'grok-2', 'silly-dragon', 'the-doge-nft', 'sillynubcat', 'based-shiba-inu', 'omnicat', 'roost', 'mog-coin', 'toshi', 'binance-peg-dogecoin', 'analos', 'conan-2', 'pepefork', 'baby-doge-coin', 'dogelon-mars', 'donald-tremp', 'vita-inu', 'volt-inu-2', 'justanegg-2', 'keyboard-cat-base', 'minu', 'bobo-coin', 'catgirl', 'wall-street-memes', 'kishu-inu', 'doginme', 'welsh-corgi-coin', 'mongcoin', 'maga', 'catwifbag', 'leash', 'snap-kero', 'kimbo', 'mumu-the-bull-3', 'bad-idea-ai', 'wojak', 'enjoy', 'love-hate-inu', 'eggdog', 'snek', 'samoyedcoin', 'defrogs', 'zyncoin-2', 'astropepex', 'mochi-thecatcoin', 'meowcat-2', 'bob-token', 'doge-eat-doge', 'harold', 'huhu-cat', 'lmeow-2', 'harambe-2', 'teddy-bear', 'mutatio-xcopyflies', 'guacamole', 'flokita']
          }

    prices = {}
    overall_market_data = {}

    # Fetch data for each category
    for category, tokens in categories.items():
        category_prices = cg.simple_prices(tokens, include_24hr_vol=True, include_24hr_change=True)
        prices[category] = category_prices.to_dict(orient='index')

        # Calculate aggregated data for the overall market
        category_volume = category_prices['usd_24h_vol'].sum()
        category_weighted_change = (category_prices['usd_24h_change'] * category_prices['usd_24h_vol']).sum() / category_volume

        # Store aggregated data for the overall market by category
        overall_market_data[category] = {
            'usd_24h_vol': category_volume,
            'weighted_24h_change': category_weighted_change
        }

    # Construct response JSON
    response_data = {
        'categories': prices,
        'overall_market': overall_market_data
    }

    return jsonify(response_data)