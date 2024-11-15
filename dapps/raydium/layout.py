from borsh_construct import CStruct, U64

from svm.layout import PublicKey

RaydiumPairClassic = CStruct(
    "status" / U64,
    "nonce" / U64,
    "order_num" / U64,
    "depth" / U64,
    "base_decimals" / U64,
    "quote_decimals" / U64,
    "state" / U64,
    "reset_flag" / U64,
    "min_size" / U64,
    "vol_max_cut_ratio" / U64,
    "amount_wave" / U64,
    "base_lot_size" / U64,
    "quote_lot_size" / U64,
    "min_price_multiplier" / U64,
    "max_price_multiplier" / U64,
    "sys_decimal_value" / U64,
    "unknown" / U64[26],
    "base_vault" / PublicKey,
    "quote_vault" / PublicKey,
    "base_mint" / PublicKey,
    "quote_mint" / PublicKey,
)
