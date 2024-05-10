// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.17;

contract OptionAssets {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum Underlying {
        BASKETS,
        STOCK_EQUITIES,
        DEBT_INSTRUMENTS,
        COMMODITIES,
        CURRENCIES,
        INDICES,
        OPTIONS,
        FUTURES,
        SWAPS,
        INTEREST_RATES,
        OTHERS
    }

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify underlying asset of the options token
    Underlying public underlyingAsset;

    constructor(Underlying _underlyingAsset) {
        underlyingAsset = _underlyingAsset;
    }
}

contract FuturesAssets {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum FinancialUnderlying {
        NONE,
        BASKETS,
        STOCK_EQUITIES,
        DEBT_INSTRUMENTS,
        CURRENCIES,
        INDICES,
        OPTIONS,
        FUTURES,
        SWAPS,
        INTEREST_RATES,
        STOCK_DIVIDEND,
        OTHERS
    }
    enum CommoditiesUnderlying {
        NONE,
        EXTRACTION_RESOURCES,
        AGRICULTURE,
        INDUSTRIAL_PRODUCTS,
        SERVICES,
        ENVIRONMENTAL,
        POLYPROPYLENE_PRODUCTS,
        GENERATED_RESOURCES,
        OTHERS
    }
    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify underlying asset of the financial future
    FinancialUnderlying public financialAsset;
    // Used to specify underlying asset of the commodities future
    CommoditiesUnderlying public commoditiesAsset;
    constructor(
        FinancialUnderlying _financialAsset,
        CommoditiesUnderlying _commoditiesAsset
    ) {
        require(
            (_financialAsset != FinancialUnderlying.NONE &&
                _commoditiesAsset == CommoditiesUnderlying.NONE) ||
                (_financialAsset == FinancialUnderlying.NONE &&
                    _commoditiesAsset != CommoditiesUnderlying.NONE),
            "Either of Financial and Commodities underlying must be NONE"
        );
        financialAsset = _financialAsset;
        commoditiesAsset = _commoditiesAsset;
    }
}
