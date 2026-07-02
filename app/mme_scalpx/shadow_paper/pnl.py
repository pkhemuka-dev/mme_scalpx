from __future__ import annotations


def calculate_long_option_metrics(
    entry_price: float,
    exit_price: float,
    highest_seen: float,
    lowest_seen: float,
    qty_lots: int,
    lot_size: int,
    assumed_slippage_points: float,
) -> dict[str, float]:
    """Long option proxy PnL.

    This local shadow-paper system assumes buying options.
    Profit is exit premium - entry premium.
    Slippage is charged on both entry and exit.
    """
    total_slippage = float(assumed_slippage_points) * 2.0
    pnl_points_net = float(exit_price) - float(entry_price) - total_slippage
    mfe_points = float(highest_seen) - float(entry_price)
    mae_points = float(lowest_seen) - float(entry_price)
    units = int(qty_lots) * int(lot_size)

    return {
        "pnl_points_net": round(pnl_points_net, 4),
        "pnl_rupees_net_proxy": round(pnl_points_net * units, 2),
        "mfe_points": round(mfe_points, 4),
        "mae_points": round(mae_points, 4),
        "mfe_rupees_proxy": round(mfe_points * units, 2),
        "mae_rupees_proxy": round(mae_points * units, 2),
        "slippage_points_total": round(total_slippage, 4),
    }
