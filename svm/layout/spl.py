from borsh_construct import CStruct, U64, U32, U16, U8, Enum, String, Option, Vec, Bool

from svm.layout import PublicKey


TokenAccount = CStruct(
    "mint" / PublicKey,
    "owner" / PublicKey,
    "amount" / U64,
    "delegate_option" / U32,
    "delegate" / PublicKey,
    "state" / U8,
    "is_native_option" / U32,
    "is_native" / U64,
    "delegated_amount" / U64,
    "close_authority_option" / U32,
    "close_authority" / PublicKey,
)

TokenMint = CStruct(
    "mint_authority_option" / U32,
    "mint_authority" / PublicKey,
    "supply" / U64,
    "decimals" / U8,
    "is_initialized" / U8,
    "freeze_authority_option" / U32,
    "freeze_authority" / PublicKey,
)

TokenMetadataKey = Enum(
    "Uninitialized",
    "EditionV1",
    "MasterEditionV1",
    "ReservationListV1",
    "MetadataV1",
    "ReservationListV2",
    "MasterEditionV2",
    "EditionMarker",
    "UseAuthorityRecord",
    "CollectionAuthorityRecord",
    "TokenOwnedEscrow",
    "TokenRecord",
    "MetadataDelegate",
    "EditionMarkerV2",
    enum_name="Key",
)

TokenMetadataCreator = CStruct("address" / PublicKey, "verified" / Bool, "share" / U8)

TokenMetadataData = CStruct(
    "name" / String,
    "symbol" / String,
    "uri" / String,
    "seller_fee_basis_points" / U16,
    "creators" / Option(Vec(TokenMetadataCreator)),
)

TokenMetadataTokenStandard = Enum(
    "NonFungible",
    "FungibleAsset",
    "Fungible",
    "NonFungibleEdition",
    "ProgrammableNonFungible",
    "ProgrammableNonFungibleEdition",
    enum_name="TokenStandard",
)

TokenMetadataCollection = CStruct("verified" / Bool, "key" / PublicKey)

TokenMetadataUseMethod = Enum("Burn", "Multiple", "Single", enum_name="UseMethod")

TokenMetadataUses = CStruct(
    "use_method" / TokenMetadataUseMethod,
    "remaining" / U64,
    "total" / U64,
)

TokenMetadataCollectionDetails = Enum(
    "V1",
    "CollectionDetailsRecordV1" / CStruct("size" / U64),
    enum_name="CollectionDetails",
)

TokenMetadataProgrammableConfig = Enum(
    "V1",
    "ProgrammableConfigRecordV1" / CStruct("rule_set" / Option(PublicKey)),
    enum_name="ProgrammableConfig",
)

TokenMetadata = CStruct(
    "key" / TokenMetadataKey,
    "update_authority" / PublicKey,
    "mint" / PublicKey,
    "data" / TokenMetadataData,
    "primary_sale_happened" / Bool,
    "is_mutable" / Bool,
    "edition_nonce" / Option(U8),
    "token_standard" / Option(TokenMetadataTokenStandard),
    "collection" / Option(TokenMetadataCollection),
    "uses" / Option(TokenMetadataUses),
    "collection_details" / Option(TokenMetadataCollectionDetails),
    "programmable_config" / Option(TokenMetadataProgrammableConfig),
)
