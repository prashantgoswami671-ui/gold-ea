"""Phase 2B environment probe.

Read-only. Connects to the running MetaTrader 5 terminal and reports the
account, terminal, available gold-like symbols and their specifications.
Writes nothing except stdout.
"""

import MetaTrader5 as mt5

ok = mt5.initialize()
print("initialize:", ok, mt5.last_error())
if not ok:
    raise SystemExit(1)

ai = mt5.account_info()
if ai is None:
    print("account: None")
else:
    print(
        "account:",
        dict(
            login=ai.login,
            server=ai.server,
            company=ai.company,
            currency=ai.currency,
            balance=ai.balance,
            leverage=ai.leverage,
            trade_allowed=ai.trade_allowed,
        ),
    )

ti = mt5.terminal_info()
if ti is None:
    print("terminal: None")
else:
    print(
        "terminal:",
        dict(
            name=ti.name,
            company=ti.company,
            path=ti.path,
            connected=ti.connected,
            build=ti.build,
            community_account=ti.community_account,
            data_path=ti.data_path,
        ),
    )

syms = mt5.symbols_get() or []
print("symbols total:", len(syms))
gold = sorted(s.name for s in syms if "XAU" in s.name.upper())
print("gold-like count:", len(gold))
print("gold-like:", gold[:30])

for name in gold[:5]:
    s = mt5.symbol_info(name)
    if s is None:
        print(name, "-> no symbol_info")
        continue
    print(
        name,
        dict(
            digits=s.digits,
            point=s.point,
            tick_size=s.trade_tick_size,
            tick_value=s.trade_tick_value,
            contract=s.trade_contract_size,
            vol_min=s.volume_min,
            vol_step=s.volume_step,
            vol_max=s.volume_max,
            stops_level=s.trade_stops_level,
            freeze=s.trade_freeze_level,
            spread_points=s.spread,
            swap_long=s.swap_long,
            swap_short=s.swap_short,
            swap_mode=s.swap_mode,
            trade_mode=s.trade_mode,
            visible=s.visible,
        ),
    )

# How much history can the terminal deliver, if the symbol is available?
for name in gold[:2]:
    for tf, label in ((mt5.TIMEFRAME_D1, "D1"), (mt5.TIMEFRAME_M15, "M15")):
        r = mt5.copy_rates_from_pos(name, tf, 0, 5)
        print(f"{name} {label} bars sample:", None if r is None else len(r))

mt5.shutdown()
