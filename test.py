# from tests.test_docs.test_generate import test_docs_generate as func
# from tests.test_jx3.test_pvx.test_horse import test_horse_list_view as func
# from tests.test_jx3.test_price.test_trade_v2 import test_single_record as func
# from tests.test_args.test_auto_args import test_auto_args as func
# func()

import test_property


async def main():
    await test_property.run()
import asyncio
asyncio.run(main())