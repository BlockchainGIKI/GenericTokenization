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

contract FinancialFuturesAssets {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum Underlying {
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

    ////////////////////
    // State Variables /
    ///////////////////
    // Used to specify underlying asset of the options token
    Underlying public underlyingAsset;

    constructor(Underlying _underlyingAsset) {
        underlyingAsset = _underlyingAsset;
    }
}

contract CommoditiesFuturesAssets {
    ///////////////////
    // Enums //////////
    ///////////////////
    enum Underlying {
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
    // Used to specify underlying asset of the options token
    Underlying public underlyingAsset;

    constructor(Underlying _underlyingAsset) {
        underlyingAsset = _underlyingAsset;
    }
}
