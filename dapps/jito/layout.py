from borsh_construct import CStruct, U8, U64

from svm.layout import PublicKey

JitoStakePool = CStruct(
    "account_type" / U8,
    "manager" / PublicKey,
    "staker" / PublicKey,
    "stake_deposit_authority" / PublicKey,
    "stake_withdraw_bump_seed" / U8,
    "validator_list" / PublicKey,
    "reserve_stake" / PublicKey,
    "pool_mint" / PublicKey,
    "manager_fee_account" / PublicKey,
    "token_program_id" / PublicKey,
    "total_lamports" / U64,
    "pool_token_supply" / U64,
)
