"""UI 좌표 일괄 측정 도구.

사용:
  1) 게임 켜고 첫 항목에 맞춰 인벤 또는 상점 UI 띄우기 (안내 따라가며 적절히 열기)
  2) python ui_probe.py
  3) 콘솔 안내 항목별로 마우스 올리고 F2 → 다음 항목 자동 이동
  4) 모든 측정 끝나면 ESC → ui_probe_params.json 저장 + 결과 출력
     macro_red.py 는 다음 실행 때 ui_probe_params.json 을 자동 적용

핫키:
  F2  = 현재 마우스 좌표 캡쳐 → 다음 항목
  F3  = 이전 항목으로 (실수 시)
  F4  = 현재 항목 건너뜀 (값 없음으로 둠)
  ESC = 결과 출력 후 종료
"""
import time
import json
import os
import ctypes
import ctypes.wintypes as wt
import keyboard

GAME_WINDOW_TITLE = 'MapleStory Worlds'
UI_PROBE_CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'ui_probe_params.json',
)


# DPI 인식
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


# 측정 대상 — (변수명, 설명, 옛 좌표 참고, mode)
# mode: 'point' = 한 점,  'rect' = 좌상단→우하단 두 점
TARGETS = [
    ('CASH_TAB_ABS',         '인벤 캐시 탭 중앙 (인벤 열고)',           (3170, 318), 'point'),
    ('PORTABLE_SHOP_ABS',    '인벤 캐시 탭 안 휴대용 상점 아이콘',       (3090, 957), 'point'),
    ('SHOP_FIRST_SLOT_ABS',  '휴대 상점 첫 슬롯 중앙 (상점 열고)',       (2060, 964), 'point'),
    ('SELL_ALL_BUTTON_ABS',  '휴대 상점 [장비 일괄 판매] 버튼',          (2564, 597), 'point'),
    ('SHOP_CLOSE_ABS',       '휴대 상점 우상단 닫기 X 버튼',             (1845, 603), 'point'),
    ('EQUIP_TAB_ABS',        '인벤 장비 탭 (상점 후 인벤 복귀용)',        (2744, 316), 'point'),
    ('ETC_TAB_ABS',          '인벤 기타 탭',                            (2488, 865), 'point'),
    ('ETC_SELL_SLOT_ABS',    '상점 안 기타템 판매 슬롯 (인벤 첫 칸 위치)',(2500, 982), 'point'),
    ('ETC_SELL_BUTTON_ABS',  '상점 안 기타템 [팔기] 버튼',               (1348, 338), 'point'),
    ('ETC_CHECK_SLOT_ABS',   '인벤 기타 탭 첫 칸 (std 체크용)',           (2058, 987), 'point'),
    ('INV_FIRST_SLOT_ABS',   '인벤 장비 탭 첫 칸',                       (2748, 406), 'point'),
    ('INV_TRIGGER_ABS',      '인벤 차있음 트리거 영역 (좌상→우하 2번)',    (3052, 910, 3147, 1007), 'rect'),
]


state = {
    'idx': 0,
    'results': {},
    'rect_buffer': None,
    'done': False,
}


def get_pos():
    pt = wt.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return pt.x, pt.y


def find_game_region(title_keyword=GAME_WINDOW_TITLE):
    try:
        import pygetwindow as gw
    except Exception:
        return None

    try:
        wins = [
            w for w in gw.getAllWindows()
            if title_keyword.lower() in (w.title or '').lower()
            and w.width > 100 and w.height > 100
        ]
        if not wins:
            return None
        w = wins[0]
        return {'left': w.left, 'top': w.top, 'width': w.width, 'height': w.height}
    except Exception:
        return None


def print_status():
    idx = state['idx']
    if idx >= len(TARGETS):
        if not state['done']:
            print('\n✅ 모든 측정 완료! ESC 누르면 결과 출력.')
            state['done'] = True
        return
    name, desc, old, mode = TARGETS[idx]
    rect_hint = ''
    if mode == 'rect':
        step = '좌상단' if state['rect_buffer'] is None else '우하단'
        rect_hint = f'  [rect — {step} 차례]'
    print(f'\n[{idx+1}/{len(TARGETS)}] {name}{rect_hint}')
    print(f'   ▸ {desc}')
    print(f'   ▸ 옛: {old}')
    print(f'   F2=캡쳐  F3=뒤로  F4=건너뜀  ESC=결과 출력')


def on_capture():
    idx = state['idx']
    if idx >= len(TARGETS):
        return
    name, desc, old, mode = TARGETS[idx]
    pos = get_pos()
    if mode == 'rect':
        if state['rect_buffer'] is None:
            state['rect_buffer'] = pos
            print(f'  ⏺ {name} 좌상단 = {pos} (이제 우하단으로 이동 후 F2)')
            return
        x1, y1 = state['rect_buffer']
        x2, y2 = pos
        # 좌상단/우하단 정렬
        rx1, rx2 = min(x1, x2), max(x1, x2)
        ry1, ry2 = min(y1, y2), max(y1, y2)
        state['results'][name] = (rx1, ry1, rx2, ry2)
        state['rect_buffer'] = None
        print(f'  ✅ {name} = ({rx1}, {ry1}, {rx2}, {ry2})')
    else:
        state['results'][name] = pos
        print(f'  ✅ {name} = {pos}')
    state['idx'] += 1
    print_status()


def on_back():
    if state['rect_buffer'] is not None:
        state['rect_buffer'] = None
        print('  ⏪ rect 좌상단 취소 → 다시 좌상단부터')
        print_status()
        return
    if state['idx'] > 0:
        state['idx'] -= 1
        name = TARGETS[state['idx']][0]
        state['results'].pop(name, None)
        state['done'] = False
        print(f'  ⏪ 이전 항목으로')
        print_status()


def on_skip():
    idx = state['idx']
    if idx >= len(TARGETS):
        return
    name = TARGETS[idx][0]
    print(f'  ⏭ {name} 건너뜀')
    state['idx'] += 1
    state['rect_buffer'] = None
    print_status()


def build_params(macro, game_region):
    params = {}

    if game_region:
        params['COORDS_CAL_GAME_LEFT'] = int(game_region['left'])
        params['COORDS_CAL_GAME_TOP'] = int(game_region['top'])
        params['COORDS_CAL_GAME_W'] = int(game_region['width'])
        params['COORDS_CAL_GAME_H'] = int(game_region['height'])
    elif macro is not None:
        params['COORDS_CAL_GAME_LEFT'] = int(getattr(macro, 'COORDS_CAL_GAME_LEFT', 0))
        params['COORDS_CAL_GAME_TOP'] = int(getattr(macro, 'COORDS_CAL_GAME_TOP', 0))
        params['COORDS_CAL_GAME_W'] = int(getattr(macro, 'COORDS_CAL_GAME_W', 1))
        params['COORDS_CAL_GAME_H'] = int(getattr(macro, 'COORDS_CAL_GAME_H', 1))

    for name, desc, old, mode in TARGETS:
        if name in state['results']:
            params[name] = [int(v) for v in state['results'][name]]
        elif macro is not None:
            value = getattr(macro, name, None)
            if isinstance(value, tuple):
                params[name] = [int(v) for v in value]

    return params


def save_params(params, game_region):
    payload = {
        'version': 1,
        'generated_by': 'ui_probe.py',
        'game_window_title': GAME_WINDOW_TITLE,
        'game_region': game_region,
        'params': params,
    }
    with open(UI_PROBE_CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f'\n[save] {UI_PROBE_CONFIG_PATH}')


def print_results():
    print('\n' + '=' * 60)
    print('  📋 측정 결과 — 아래 python 블록을 macro_red.py 에 그대로 붙여넣으세요')
    print('=' * 60)

    macro = None
    game_region = find_game_region()
    try:
        import macro_red as m
        macro = m
        if game_region is None:
            m.refresh_game_region()
            game_region = m.GAME_REGION
    except Exception as e:
        print(f'# [warn] macro_red import/refresh 실패: {e!r}')

    params = build_params(macro, game_region)
    save_params(params, game_region)

    def as_tuple_text(value):
        return repr(tuple(int(v) for v in value))

    def fallback_value(name):
        if macro is None:
            return None
        value = getattr(macro, name, None)
        if isinstance(value, tuple):
            return value
        return None

    print('```python')
    print('# === BEGIN UI_PROBE_PARAMS ===')
    print('# ui_probe.py 출력값입니다. macro_red.py 의 같은 구간에 그대로 붙여넣을 수도 있습니다.')
    print('# 보통은 ui_probe_params.json 이 자동 저장되므로 붙여넣지 않아도 됩니다.')

    for name in ('COORDS_CAL_GAME_LEFT', 'COORDS_CAL_GAME_TOP',
                 'COORDS_CAL_GAME_W', 'COORDS_CAL_GAME_H'):
        if name in params:
            print(f'{name:22s} = {params[name]}')
        else:
            print(f'# {name:20s} = <missing>')

    for name, desc, old, mode in TARGETS:
        if name in params:
            print(f'{name:22s} = {as_tuple_text(params[name])}')
        else:
            print(f'# {name:20s} = <skipped>')

    print('# === END UI_PROBE_PARAMS ===')
    print('```')


def main():
    print('=' * 60)
    print('  UI 좌표 일괄 측정 도구')
    print('=' * 60)
    print('  F2  = 현재 마우스 좌표 캡쳐')
    print('  F3  = 이전 항목으로 (실수 시)')
    print('  F4  = 현재 항목 건너뜀')
    print('  ESC = 결과 출력 후 종료')
    print()
    print('▶ 시작 전: 게임에서 인벤토리 열어두세요 (Ctrl+I 보통)')
    print('▶ 항목별 안내에 따라 적절히 상점도 열고 닫으며 진행')
    print('▶ 측정 도중 ESC 눌러도 그때까지의 결과가 ui_probe_params.json 으로 저장됩니다')

    keyboard.add_hotkey('f2', on_capture)
    keyboard.add_hotkey('f3', on_back)
    keyboard.add_hotkey('f4', on_skip)

    print_status()

    try:
        keyboard.wait('esc')
    except KeyboardInterrupt:
        pass

    print_results()


if __name__ == '__main__':
    main()
