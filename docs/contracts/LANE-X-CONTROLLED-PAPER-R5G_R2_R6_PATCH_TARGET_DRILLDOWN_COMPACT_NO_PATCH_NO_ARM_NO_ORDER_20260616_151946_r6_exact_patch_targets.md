# LANE-X-CONTROLLED-PAPER-R5G_R2_R6_PATCH_TARGET_DRILLDOWN_COMPACT_NO_PATCH_NO_ARM_NO_ORDER_20260616_151946

## Purpose
Exact R6 patch target drilldown before writing any patch.

## Current verdict
Controlled paper is NOT ready to arm.

## R6 goal
Publish fail-closed runtime status only. Do not arm paper.

## Required surfaces
- Position: has_position=0, position_side=FLAT, qty_lots=0, qty_units=0
- Risk: CONTROLLED_PAPER_NOT_ARMED, controlled_paper_entry_veto=1, position_open=0, trades_today=0
- Execution: entry_pending=0, exit_pending=0, pending_order_json empty, last_error empty
- Paper gate: paper_armed=false, route_allowed=false, paper_allowed=false, pstatus/paper_status visible

## Target groups
{
  "execution": {
    "app/mme_scalpx/core/names.py": [
      784
    ],
    "app/mme_scalpx/services/execution.py": [
      557,
      605,
      856,
      997,
      1091,
      1118,
      1149,
      1333,
      1432,
      1469,
      1492,
      1548,
      1608,
      1772
    ]
  },
  "paper_gate": {
    "app/mme_scalpx/integrations/bootstrap_quote.py": [
      78,
      79
    ],
    "app/mme_scalpx/integrations/broker_api.py": [
      1437,
      1492,
      1511,
      1540,
      1543
    ],
    "app/mme_scalpx/main.py": [
      128,
      1131,
      1132
    ],
    "app/mme_scalpx/ops_dashboard/server.py": [
      44,
      45,
      536,
      537
    ],
    "app/mme_scalpx/services/controlled_paper_observability.py": [
      17,
      19,
      23,
      53,
      66,
      76,
      83,
      88,
      95,
      96,
      107,
      110
    ],
    "app/mme_scalpx/services/controlled_paper_route.py": [
      16,
      17,
      22,
      26,
      75,
      90,
      92,
      93,
      99,
      101,
      115,
      118,
      121
    ],
    "app/mme_scalpx/services/controlled_paper_runtime.py": [
      12,
      13,
      14,
      16,
      18,
      19,
      124,
      172,
      174,
      215,
      219,
      223,
      269,
      353,
      422
    ],
    "app/mme_scalpx/services/execution.py": [
      172,
      2084,
      2159,
      2160,
      2642,
      2643,
      2644,
      2645,
      2646,
      2647,
      2648,
      2649,
      2674,
      2698,
      2722,
      2727,
      2730,
      2738,
      2744,
      2747,
      2753,
      2762,
      2776,
      2777,
      2797,
      2806
    ],
    "app/mme_scalpx/services/risk.py": [
      1054,
      2216,
      2219,
      2220,
      2221,
      2222,
      2223,
      2328,
      2333,
      2431,
      2441,
      2442,
      2444,
      2465,
      2471,
      2474,
      2479,
      2484,
      2493,
      2499,
      2502,
      2511,
      2514,
      2532,
      2534,
      2537,
      2539,
      2540,
      2547
    ],
    "app/mme_scalpx/services/strategy.py": [
      244,
      877,
      878,
      1098,
      1099,
      1553,
      1596,
      1947,
      1948,
      1991,
      1995,
      1998,
      1999,
      2000,
      2002,
      2003,
      2039,
      2065,
      2090,
      2091,
      2094,
      2095,
      2096,
      2099,
      2146,
      2173,
      2193,
      2196,
      2212,
      2214,
      2223,
      2225,
      2253,
      2254,
      2302,
      2332,
      2353,
      2398,
      2399,
      2444,
      2448
    ],
    "app/mme_scalpx/services/strategy_family/common.py": [
      1069,
      1070
    ],
    "app/mme_scalpx/services/strategy_family/internal_order_intent_pipeline.py": [
      28,
      29
    ],
    "scripts/r38aj_mist_near_candidate_shadow_export.py": [
      172,
      254
    ],
    "scripts/r38ak_mist_near_candidate_timestamp_pnl.py": [
      109,
      204
    ],
    "scripts/r38al_mist_near_parent_ts_shadow_pnl.py": [
      185,
      307
    ],
    "scripts/r38am_option_raw_field_parser_shadow_pnl.py": [
      208
    ],
    "scripts/r38ao_option_blank_value_safe_parser_shadow_pnl.py": [
      221
    ],
    "scripts/r38ap_mist_near_cost_dedup_segment_audit.py": [
      137
    ],
    "scripts/r38aq_r2_evidence_derived_mist_put_near_profile.py": [
      151,
      203,
      212
    ],
    "scripts/r38au_r2_misc_compression_diagnostic.py": [
      209,
      210
    ],
    "scripts/r38ba_all_strategy_both_side_live_shadow_gate.py": [
      204,
      242
    ]
  },
  "position": {
    "app/mme_scalpx/core/models.py": [
      2513,
      2514,
      2538,
      2539,
      2573,
      2575,
      2586,
      2883,
      2908,
      2909
    ],
    "app/mme_scalpx/core/names.py": [
      783
    ],
    "app/mme_scalpx/integrations/provider_runtime.py": [
      846,
      873
    ],
    "app/mme_scalpx/ops/healthcheck.py": [
      226
    ],
    "app/mme_scalpx/research_capture/contracts.py": [
      662
    ],
    "app/mme_scalpx/research_capture/models.py": [
      659
    ],
    "app/mme_scalpx/services/execution.py": [
      569,
      570,
      632,
      633,
      634,
      1029,
      1035,
      1036,
      1037,
      1247,
      1357,
      1530,
      1531,
      1564,
      1594,
      1595,
      1624,
      1677,
      1701,
      1719,
      1938,
      1956,
      2667,
      2668,
      2669
    ],
    "app/mme_scalpx/services/monitor.py": [
      449,
      450,
      459,
      460,
      530,
      531,
      803,
      804,
      811,
      812,
      816,
      817,
      914,
      916,
      930,
      965,
      971,
      972
    ],
    "app/mme_scalpx/services/report.py": [
      744
    ],
    "app/mme_scalpx/services/risk.py": [
      672,
      673,
      674,
      1484,
      1485,
      1486,
      2381,
      2385,
      2402,
      2403,
      2404
    ],
    "app/mme_scalpx/services/strategy.py": [
      2005
    ],
    "app/mme_scalpx/services/strategy_family/common.py": [
      443,
      445,
      446,
      448,
      1157
    ],
    "app/mme_scalpx/services/strategy_family/doctrine_runtime.py": [
      313,
      314,
      323,
      324,
      338,
      339,
      347,
      348,
      349,
      364,
      365
    ],
    "app/mme_scalpx/services/strategy_legacy_single.py": [
      342,
      343,
      373,
      397,
      460,
      539,
      672,
      678,
      693,
      704,
      740,
      781,
      882,
      1051,
      1085,
      1147,
      1153,
      1188,
      1201,
      1280,
      1282,
      1537,
      1538,
      1548,
      1549
    ]
  },
  "redis_write": {
    "app/mme_scalpx/core/redisx.py": [
      243,
      245,
      246,
      247,
      248,
      249,
      250,
      251,
      254,
      255,
      257,
      259,
      260,
      269,
      271,
      276,
      278,
      283,
      285,
      358,
      361,
      363,
      364,
      368,
      371,
      373,
      374,
      534,
      562,
      666,
      696,
      710,
      719,
      725,
      731,
      739,
      742,
      751,
      757,
      763,
      772,
      784,
      800,
      886,
      897,
      902,
      929,
      940,
      945,
      975,
      988,
      993,
      1026,
      1039,
      1044,
      1557,
      1581,
      1758,
      1791
    ],
    "app/mme_scalpx/core/settings.py": [
      837,
      1163,
      1183,
      1211,
      1455
    ],
    "app/mme_scalpx/main.py": [
      1060,
      1066
    ],
    "app/mme_scalpx/ops/ops_cmd.py": [
      228
    ],
    "app/mme_scalpx/replay/safety.py": [
      49,
      50,
      66,
      67
    ],
    "app/mme_scalpx/services/execution.py": [
      1821,
      1854,
      1888,
      1918,
      1959,
      1979,
      1998,
      2123,
      2124,
      2127,
      2455,
      2877
    ],
    "app/mme_scalpx/services/features.py": [
      4353,
      4355,
      4376,
      4384,
      4394,
      4416,
      4419,
      4437,
      7118,
      7398,
      7557,
      7752,
      7859,
      7860,
      7863,
      7878,
      7879,
      7887,
      7923,
      7924,
      7955,
      7957,
      8028,
      8029,
      8037,
      8071,
      8072,
      8094,
      8189,
      8191,
      8192,
      8222
    ],
    "app/mme_scalpx/services/feeds.py": [
      1916,
      1923,
      1947,
      2274,
      2509,
      2530,
      2909,
      2977,
      2982,
      2986,
      3067,
      3068,
      3072,
      3102,
      3103
    ],
    "app/mme_scalpx/services/monitor.py": [
      67,
      640
    ],
    "app/mme_scalpx/services/report.py": [
      68
    ],
    "app/mme_scalpx/services/risk.py": [
      987,
      1008,
      1093,
      1094,
      1097,
      2132,
      2155
    ],
    "app/mme_scalpx/services/strategy.py": [
      472,
      478,
      1302,
      1317,
      1408,
      1427,
      1430,
      1450
    ],
    "app/mme_scalpx/services/strategy_legacy_single.py": [
      1415,
      1430,
      1560
    ]
  },
  "redis_writes": {
    "app/mme_scalpx/replay/safety.py": [
      51,
      68
    ]
  },
  "risk": {
    "app/mme_scalpx/core/models.py": [
      2671,
      2688
    ],
    "app/mme_scalpx/core/names.py": [
      782
    ],
    "app/mme_scalpx/ops/healthcheck.py": [
      230,
      232
    ],
    "app/mme_scalpx/services/execution.py": [
      393,
      1258,
      1643,
      1645,
      1649
    ],
    "app/mme_scalpx/services/monitor.py": [
      497,
      507,
      529,
      547,
      792,
      793,
      871,
      911,
      929,
      944,
      1029,
      1230,
      1265
    ],
    "app/mme_scalpx/services/risk.py": [
      69,
      76,
      484,
      687,
      691,
      694,
      697,
      700,
      703,
      709,
      715,
      718,
      721,
      724,
      727,
      730,
      898,
      918,
      970,
      1516,
      1520,
      1523,
      1526,
      1529,
      1532,
      1538,
      1544,
      1547,
      1550,
      1553,
      1556,
      1559,
      1562,
      1565,
      1568,
      2011,
      2030,
      2097,
      2218,
      2451,
      2468,
      2495,
      2533,
      2536
    ],
    "app/mme_scalpx/services/strategy_family/doctrine_runtime.py": [
      257,
      279
    ],
    "app/mme_scalpx/services/strategy_legacy_single.py": [
      321,
      582,
      831,
      1495,
      1506
    ]
  }
}

## Required tests after R6
1. Static compile/import
2. No-order fixture
3. Runtime observe-only publication proof
4. Controlled-paper gate verdict
5. Explicit user approval before any separate arming command

## Source snippets
run/audits/LANE-X-CONTROLLED-PAPER-R5G_R2_R6_PATCH_TARGET_DRILLDOWN_COMPACT_NO_PATCH_NO_ARM_NO_ORDER_20260616_151946_source_snippets.txt
