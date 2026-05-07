WORKSPACES = [
    {"id": "ws-001", "name": "ESM Risk & Finance", "state": "Active"},
    {"id": "ws-002", "name": "Portfolio Analytics", "state": "Active"},
]

REPORTS = [
    {
        "id": "rpt-001",
        "name": "ESM Middle Office Dashboard",
        "datasetId": "ds-001",
        "workspaceId": "ws-001",
        "webUrl": "https://app.powerbi.com/reports/rpt-001",
        "pages": [
            {"name": "Overview",     "displayName": "Executive Overview",    "order": 1},
            {"name": "CreditRisk",   "displayName": "Credit Risk Monitor",   "order": 2},
            {"name": "Liquidity",    "displayName": "Liquidity Dashboard",   "order": 3},
            {"name": "Counterparty", "displayName": "Counterparty Exposure", "order": 4},
        ],
    },
    {
        "id": "rpt-002",
        "name": "Credit Scorecard Report",
        "datasetId": "ds-002",
        "workspaceId": "ws-002",
        "webUrl": "https://app.powerbi.com/reports/rpt-002",
        "pages": [
            {"name": "Scorecard", "displayName": "Credit Scorecard",        "order": 1},
            {"name": "SHAP",      "displayName": "SHAP Feature Importance", "order": 2},
            {"name": "RiskBands", "displayName": "Risk Band Distribution",  "order": 3},
        ],
    },
    {
        "id": "rpt-003",
        "name": "Fund Risk Intelligence",
        "datasetId": "ds-003",
        "workspaceId": "ws-002",
        "webUrl": "https://app.powerbi.com/reports/rpt-003",
        "pages": [
            {"name": "Anomalies", "displayName": "Anomaly Detection", "order": 1},
            {"name": "Forecast",  "displayName": "Prophet Forecast",  "order": 2},
        ],
    },
]

DATASETS = [
    {
        "id": "ds-001",
        "name": "ESM_MiddleOffice",
        "workspaceId": "ws-001",
        "configuredBy": "Mohammed Khaled",
        "isRefreshable": True,
        "tables": [
            {
                "name": "FactTransactions",
                "columns": [
                    {"name": "TransactionId",  "dataType": "Int64"},
                    {"name": "CounterpartyId", "dataType": "Int64"},
                    {"name": "InstrumentType", "dataType": "String"},
                    {"name": "Notional",       "dataType": "Decimal"},
                    {"name": "TradeDate",      "dataType": "DateTime"},
                    {"name": "MaturityDate",   "dataType": "DateTime"},
                    {"name": "CreditRating",   "dataType": "String"},
                    {"name": "ExposureEUR",    "dataType": "Decimal"},
                    {"name": "RiskWeight",     "dataType": "Decimal"},
                ],
            },
            {
                "name": "DimCounterparty",
                "columns": [
                    {"name": "CounterpartyId",   "dataType": "Int64"},
                    {"name": "CounterpartyName", "dataType": "String"},
                    {"name": "Country",          "dataType": "String"},
                    {"name": "Sector",           "dataType": "String"},
                    {"name": "InternalRating",   "dataType": "String"},
                ],
            },
            {
                "name": "DimDate",
                "columns": [
                    {"name": "Date",      "dataType": "DateTime"},
                    {"name": "Year",      "dataType": "Int64"},
                    {"name": "Quarter",   "dataType": "String"},
                    {"name": "Month",     "dataType": "Int64"},
                    {"name": "MonthName", "dataType": "String"},
                ],
            },
        ],
    },
    {
        "id": "ds-002",
        "name": "CreditScorecard_Basel3",
        "workspaceId": "ws-002",
        "configuredBy": "Mohammed Khaled",
        "isRefreshable": True,
        "tables": [
            {
                "name": "FactLoans",
                "columns": [
                    {"name": "LoanId",      "dataType": "Int64"},
                    {"name": "CustomerId",  "dataType": "Int64"},
                    {"name": "LoanAmount",  "dataType": "Decimal"},
                    {"name": "PD_Score",    "dataType": "Decimal"},
                    {"name": "LGD",         "dataType": "Decimal"},
                    {"name": "EAD",         "dataType": "Decimal"},
                    {"name": "RiskBand",    "dataType": "String"},
                    {"name": "DefaultFlag", "dataType": "Boolean"},
                ],
            },
            {
                "name": "FactSHAP",
                "columns": [
                    {"name": "LoanId",         "dataType": "Int64"},
                    {"name": "Feature",        "dataType": "String"},
                    {"name": "SHAPValue",      "dataType": "Decimal"},
                    {"name": "ImportanceRank", "dataType": "Int64"},
                ],
            },
        ],
    },
    {
        "id": "ds-003",
        "name": "FundRisk_Intelligence",
        "workspaceId": "ws-002",
        "configuredBy": "Mohammed Khaled",
        "isRefreshable": False,
        "tables": [
            {
                "name": "FactFundReturns",
                "columns": [
                    {"name": "FundId",         "dataType": "Int64"},
                    {"name": "Date",           "dataType": "DateTime"},
                    {"name": "Return",         "dataType": "Decimal"},
                    {"name": "AnomalyScore",   "dataType": "Decimal"},
                    {"name": "IsAnomaly",      "dataType": "Boolean"},
                    {"name": "ForecastReturn", "dataType": "Decimal"},
                ],
            },
        ],
    },
]

MEASURES = [
    {
        "id": "m-001", "datasetId": "ds-001", "name": "Total Exposure EUR",
        "table": "FactTransactions",
        "expression": "SUM(FactTransactions[ExposureEUR])",
        "description": "Sum of all counterparty exposures in EUR",
    },
    {
        "id": "m-002", "datasetId": "ds-001", "name": "Weighted Risk Score",
        "table": "FactTransactions",
        "expression": "SUMX(FactTransactions, FactTransactions[ExposureEUR] * FactTransactions[RiskWeight]) / [Total Exposure EUR]",
        "description": "Exposure-weighted average risk weight across portfolio",
    },
    {
        "id": "m-003", "datasetId": "ds-001", "name": "High Risk Exposure",
        "table": "FactTransactions",
        "expression": "CALCULATE([Total Exposure EUR], FactTransactions[CreditRating] IN {\"CCC\",\"CC\",\"C\",\"D\"})",
        "description": "Total exposure to sub-investment grade counterparties",
    },
    {
        "id": "m-004", "datasetId": "ds-002", "name": "Average PD",
        "table": "FactLoans",
        "expression": "AVERAGE(FactLoans[PD_Score])",
        "description": "Portfolio average probability of default",
    },
    {
        "id": "m-005", "datasetId": "ds-002", "name": "Expected Loss",
        "table": "FactLoans",
        "expression": "SUMX(FactLoans, FactLoans[PD_Score] * FactLoans[LGD] * FactLoans[EAD])",
        "description": "Basel III expected loss: PD x LGD x EAD",
    },
    {
        "id": "m-006", "datasetId": "ds-002", "name": "Default Rate",
        "table": "FactLoans",
        "expression": "DIVIDE(COUNTROWS(FILTER(FactLoans, FactLoans[DefaultFlag] = TRUE())), COUNTROWS(FactLoans))",
        "description": "Observed default rate in the loan portfolio",
    },
    {
        "id": "m-007", "datasetId": "ds-003", "name": "Anomaly Rate",
        "table": "FactFundReturns",
        "expression": "DIVIDE(COUNTROWS(FILTER(FactFundReturns, FactFundReturns[IsAnomaly] = TRUE())), COUNTROWS(FactFundReturns))",
        "description": "Proportion of fund return observations flagged as anomalies",
    },
    {
        "id": "m-008", "datasetId": "ds-003", "name": "Avg Anomaly Score",
        "table": "FactFundReturns",
        "expression": "AVERAGE(FactFundReturns[AnomalyScore])",
        "description": "Average Isolation Forest anomaly score across all observations",
    },
]