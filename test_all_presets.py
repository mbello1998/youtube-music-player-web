# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5050')
    page.wait_for_timeout(2000)
    page.evaluate('openStemsModal();')
    page.wait_for_timeout(500)
    
    presets = ['vocal', 'beat', 'inst', 'basskill', 'bassonly', 'harmonly', 'full']
    res = {}
    for pr in presets:
        page.evaluate(f"applyStemPreset('{pr}');")
        st = page.evaluate("""() => {
            return {
                dry: window.stemsDryGain.gain.value,
                vocal: window.stemGain_vocal.gain.value,
                drums: window.stemGain_drums.gain.value,
                bass: window.stemGain_bass.gain.value,
                inst: window.stemGain_inst.gain.value
            };
        }""")
        res[pr] = st
    print('Presets verification:', res)
    for pr, val in res.items():
        print(f"Preset {pr:10}: Dry={val['dry']:.2f}, Vocal={val['vocal']:.2f}, Drums={val['drums']:.2f}, Bass={val['bass']:.2f}, Inst={val['inst']:.2f}")
