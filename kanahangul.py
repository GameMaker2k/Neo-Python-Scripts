from __future__ import annotations
from pathlib import Path
import re

def _read_text_source(text: str | None = None, file: str | Path | None = None, *, encoding: str = "utf-8") -> str:
    """Read input from either a text string or a file path.

    Exactly one of `text` or `file` should be provided.
    """
    if (text is None) == (file is None):
        raise ValueError("Provide exactly one of `text` or `file`.")
    if file is not None:
        return Path(file).read_text(encoding=encoding)
    return text or ""

def _write_text_dest(result: str, out_file: str | Path | None = None, *, encoding: str = "utf-8") -> str:
    """Optionally write result to `out_file`. Returns the result string."""
    if out_file is not None:
        Path(out_file).write_text(result, encoding=encoding)
    return result

import copy

# ============================================================
#  Kana -> Hangul mapping (BASE)
# ============================================================

kana_to_hangul_base: dict[str, str] = {
    # --- Basic vowels (incl. small vowels) ---
    "あ": "아", "ア": "아",
    "ぁ": "아", "ァ": "아",
    "い": "이", "イ": "이",
    "ぃ": "이", "ィ": "이",
    "う": "우", "ウ": "우",
    "ぅ": "우", "ゥ": "우",
    "え": "에", "エ": "에",
    "ぇ": "에", "ェ": "에",
    "お": "오", "オ": "오",
    "ぉ": "오", "ォ": "오",

    # --- K row ---
    "か": "카", "カ": "카",
    "き": "키", "キ": "키",
    "く": "쿠", "ク": "쿠",
    "け": "케", "ケ": "케",
    "こ": "코", "コ": "코",

    # K + small ya/yu/yo
    "きゃ": "캬", "キャ": "캬",
    "きゅ": "큐", "キュ": "큐",
    "きょ": "쿄", "キョ": "쿄",

    # --- S row ---
    "さ": "사", "サ": "사",
    "し": "시", "シ": "시",
    "す": "스", "ス": "스",
    "せ": "세", "セ": "세",
    "そ": "소", "ソ": "소",

    # SH + small ya/yu/yo
    "しゃ": "샤", "シャ": "샤",
    "しゅ": "슈", "シュ": "슈",
    "しょ": "쇼", "ショ": "쇼",

    # --- T row ---
    "た": "타", "タ": "타",
    "ち": "치", "チ": "치",
    "つ": "츠", "ツ": "츠",
    "て": "테", "テ": "테",
    "と": "토", "ト": "토",

    # CH + small ya/yu/yo
    "ちゃ": "챠", "チャ": "챠",
    "ちゅ": "츄", "チュ": "츄",
    "ちょ": "쵸", "チョ": "쵸",

    # --- N row ---
    "な": "나", "ナ": "나",
    "に": "니", "ニ": "니",
    "ぬ": "누", "ヌ": "누",
    "ね": "네", "ネ": "네",
    "の": "노", "ノ": "노",
    "ん": "ㄴ", "ン": "ㄴ",

    # N + small ya/yu/yo
    "にゃ": "냐", "ニャ": "냐",
    "にゅ": "뉴", "ニュ": "뉴",
    "にょ": "뇨", "ニョ": "뇨",

    # --- H row ---
    "は": "하", "ハ": "하",
    "ひ": "히", "ヒ": "히",
    "ふ": "후", "フ": "후",
    "へ": "헤", "ヘ": "헤",
    "ほ": "호", "ホ": "호",

    # H + small ya/yu/yo
    "ひゃ": "햐", "ヒャ": "햐",
    "ひゅ": "휴", "ヒュ": "휴",
    "ひょ": "효", "ヒョ": "효",

    # --- M row ---
    "ま": "마", "マ": "마",
    "み": "미", "ミ": "미",
    "む": "무", "ム": "무",
    "め": "메", "メ": "메",
    "も": "모", "モ": "모",

    # M + small ya/yu/yo
    "みゃ": "먀", "ミャ": "먀",
    "みゅ": "뮤", "ミュ": "뮤",
    "みょ": "묘", "ミョ": "묘",

    # --- Y row ---
    "や": "야", "ヤ": "야",
    "ゃ": "야", "ャ": "야",
    "ゆ": "유", "ユ": "유",
    "ゅ": "유", "ュ": "유",
    "よ": "요", "ヨ": "요",
    "ょ": "요", "ョ": "요",

    # --- R row ---
    "ら": "라", "ラ": "라",
    "り": "리", "リ": "리",
    "る": "루", "ル": "루",
    "れ": "레", "レ": "레",
    "ろ": "로", "ロ": "로",

    # R + small ya/yu/yo
    "りゃ": "랴", "リャ": "랴",
    "りゅ": "류", "リュ": "류",
    "りょ": "료", "リョ": "료",

    # --- W row & historical ---
    "わ": "와", "ワ": "와",
    "を": "오", "ヲ": "오",
    "ゑ": "웨", "ヱ": "웨",
    "ゐ": "위", "ヰ": "위",

    

    # Vu (added)
    "ゔ": "부", "ヴ": "부",# --- G row ---
    "が": "가", "ガ": "가",
    "ぎ": "기", "ギ": "기",
    "ぐ": "구", "グ": "구",
    "げ": "게", "ゲ": "게",
    "ご": "고", "ゴ": "고",

    # G + small ya/yu/yo
    "ぎゃ": "갸", "ギャ": "갸",
    "ぎゅ": "규", "ギュ": "규",
    "ぎょ": "교", "ギョ": "교",

    # --- Z/J row ---
    "ざ": "자", "ザ": "자",
    "じ": "지", "ジ": "지",
    "ず": "즈", "ズ": "즈",
    "ぜ": "제", "ゼ": "제",
    "ぞ": "조", "ゾ": "조",

    # J + small ya/yu/yo
    "じゃ": "쟈", "ジャ": "쟈",
    "じゅ": "쥬", "ジュ": "쥬",
    "じょ": "죠", "ジョ": "죠",

    # --- D row ---
    "だ": "다", "ダ": "다",
    "ぢ": "지", "ヂ": "지",
    "づ": "즈", "ヅ": "즈",
    "で": "데", "デ": "데",
    "ど": "도", "ド": "도",

    # --- B row ---
    "ば": "바", "バ": "바",
    "び": "비", "ビ": "비",
    "ぶ": "부", "ブ": "부",
    "べ": "베", "ベ": "베",
    "ぼ": "보", "ボ": "보",

    # B + small ya/yu/yo
    "びゃ": "뱌", "ビャ": "뱌",
    "びゅ": "뷰", "ビュ": "뷰",
    "びょ": "뵤", "ビョ": "뵤",

    # --- P row ---
    "ぱ": "파", "パ": "파",
    "ぴ": "피", "ピ": "피",
    "ぷ": "푸", "プ": "푸",
    "ぺ": "페", "ペ": "페",
    "ぽ": "포", "ポ": "포",

    # P + small ya/yu/yo
    "ぴゃ": "퍄", "ピャ": "퍄",
    "ぴゅ": "퓨", "ピュ": "퓨",
    "ぴょ": "표", "ピョ": "표",
}

# ============================================================
# Ready-made Hangul profile overrides (edit/extend freely)
# Drop this into your script as-is.
# ============================================================

hangul_profile_overrides: dict[str, dict[str, str]] = {
    # --------------------------------------------------------
    # Base: your original mapping (no overrides)
    # --------------------------------------------------------
    "default": {},

    # --------------------------------------------------------
    # Profile: "strict" (keep it conservative / round-trip friendly)
    # - stays close to your current outputs
    # --------------------------------------------------------
    "strict": {
        # (intentionally empty; keep base behavior)
    },

    # --------------------------------------------------------
    # Profile: "loanword_kr" (more like common Korean loanword feel)
    # Notes:
    # - し/シ often still ends up "시" in Korean, but some people prefer
    #   stronger "씨" to suggest /shi/; here we KEEP "시".
    # - つ/ツ is often perceived closer to "츠" than "쓰" for Japanese tsu.
    # - ふ/フ sometimes written "후" (default) vs "푸"; keep "후".
    # --------------------------------------------------------
    "loanword_kr": {
        # keep defaults; but you can tune the "fu" feeling if you want:
        # "ふ": "후", "フ": "후",  # default already
        # or:
        # "ふ": "푸", "フ": "푸",
    },

    # --------------------------------------------------------
    # Profile: "shi_ssi"
    # - force し/シ and sh- combinations to "씨/쌰/쓔/쑈"
    # - this emphasizes the stronger frication some learners want
    # --------------------------------------------------------
    "shi_ssi": {
        "し": "씨", "シ": "씨",
        "しゃ": "쌰", "シャ": "쌰",
        "しゅ": "쓔", "シュ": "쓔",
        "しょ": "쑈", "ショ": "쑈",
    },

    # --------------------------------------------------------
    # Profile: "tsu_sseu"
    # - make つ/ツ become 쓰 (instead of 츠)
    # - useful if you prefer to avoid the "츠" look
    # --------------------------------------------------------
    "tsu_sseu": {
        "つ": "쓰", "ツ": "쓰",
    },

    # Combine styles as another profile example
    "shi_ssi_tsu_sseu": {
        "し": "씨", "シ": "씨",
        "しゃ": "쌰", "シャ": "쌰",
        "しゅ": "쓔", "シュ": "쓔",
        "しょ": "쑈", "ショ": "쑈",
        "つ": "쓰", "ツ": "쓰",
    },

    # --------------------------------------------------------
    # Profile: "ja_simple"
    # - make じゃ/じゅ/じょ map to 자/주/조 (less "foreign-looking")
    # - rather than 쟈/쥬/죠
    # --------------------------------------------------------
    "ja_simple": {
        "じゃ": "자", "ジャ": "자",
        "じゅ": "주", "ジュ": "주",
        "じょ": "조", "ジョ": "조",
    },

    # --------------------------------------------------------
    # Profile: "cha_chya"
    # - some prefer ちゃ/チャ to be "차" not "챠"
    # - and similarly ちゅ/ちょ
    # --------------------------------------------------------
    "cha_chya": {
        "ちゃ": "차", "チャ": "차",
        "ちゅ": "추", "チュ": "추",
        "ちょ": "초", "チョ": "초",
    },

    # --------------------------------------------------------
    # Profile: "korean_media"
    # - a more "Korean viewer" feel:
    #   * strong shi -> 씨
    #   * tsu -> 쓰
    #   * ja -> 자/주/조
    #   * optionally cha -> 차/추/초
    # --------------------------------------------------------
    "korean_media": {
        "し": "씨", "シ": "씨",
        "しゃ": "쌰", "シャ": "쌰",
        "しゅ": "쓔", "シュ": "쓔",
        "しょ": "쑈", "ショ": "쑈",
        "つ": "쓰", "ツ": "쓰",
        "じゃ": "자", "ジャ": "자",
        "じゅ": "주", "ジュ": "주",
        "じょ": "조", "ジョ": "조",
        # Uncomment if you prefer "cha" without the palatalized look:
        # "ちゃ": "차", "チャ": "차",
        # "ちゅ": "추", "チュ": "추",
        # "ちょ": "초", "チョ": "초",
    },

    # --------------------------------------------------------
    # Profile: "my_roundtrip_safe_plus"
    # - tiny changes that usually still round-trip well:
    #   * keep shi as 시 (default)
    #   * keep tsu as 츠 (default)
    #   * change only "fu" if desired
    # --------------------------------------------------------
    "my_roundtrip_safe_plus": {
        # You can pick ONE:
        # "ふ": "후", "フ": "후",  # default
        # "ふ": "푸", "フ": "푸",  # alternate
    },
}

KANA_TO_HANGUL_PROFILES: dict[str, dict[str, str]] = {}
for profile_name, overrides in hangul_profile_overrides.items():
    d = copy.deepcopy(kana_to_hangul_base)
    d.update(overrides)
    KANA_TO_HANGUL_PROFILES[profile_name] = d


# ============================================================
# Hangul <-> Korean Romanization systems (separate from JP romaji)
# ============================================================
#
# This module already includes Japanese kana<->romaji utilities. The following
# section adds Korean Hangul<->Latin romanization utilities that are *system*
# aware (RR, MR, Yale, etc.) using dict-based tables.
#
# Design goal: "round-trip" for text produced by `hangul_to_kroman_text` when
# decoded with `kroman_to_hangul_text`, especially when using a syllable
# separator (default "-") to avoid ambiguity across syllable boundaries.

# System tables are based on the standard consonant/vowel correspondences for:
# - Revised Romanization (RR) (South Korea, 2000)
# - McCune–Reischauer (MR) (1939) and MR-derived variants (incl. NK 1992)
# - Yale romanization (linguistics)
# - ALA-LC (library cataloging; MR-derived)
#
# Note: Full "pronunciation-based" rules (liaison, assimilation, etc.) vary by
# system and context. For reversibility we intentionally implement a *letter-by-letter*
# (syllable-by-syllable) transliteration variant, not a phonological one.

KROMAN_SYSTEMS: dict[str, dict[str, object]] = {
    "rr": {
        "name": "Revised Romanization of Korean",
        "abbr": "RR",
        "year": 2000,
        "notes": "Syllable-by-syllable reversible variant (no phonological rules).",
        "onset": {
            "": 11,   # ㅇ
            "g": 0, "kk": 1, "n": 2, "d": 3, "tt": 4, "r": 5, "m": 6,
            "b": 7, "pp": 8, "s": 9, "ss": 10, "j": 12, "jj": 13, "ch": 14,
            "k": 15, "t": 16, "p": 17, "h": 18,
        },
        "vowel": {
            "a": 0, "ae": 1, "ya": 2, "yae": 3, "eo": 4, "e": 5, "yeo": 6, "ye": 7,
            "o": 8, "wa": 9, "wae": 10, "oe": 11, "yo": 12,
            "u": 13, "wo": 14, "we": 15, "wi": 16, "yu": 17,
            "eu": 18, "ui": 19, "i": 20,
        },
        "coda": {
            "": 0,
            "k": 1, "kk": 2, "ks": 3, "n": 4, "nj": 5, "nh": 6, "t": 7,
            "l": 8, "lk": 9, "lm": 10, "lb": 11, "ls": 12, "lt": 13, "lp": 14, "lh": 15,
            "m": 16, "p": 17, "ps": 18, "t_s": 19, "t_ss": 20, "ng": 21,
            "t_j": 22, "t_ch": 23, "k_kh": 24, "t_th": 25, "p_ph": 26, "t_h": 27,
        },
        # romanization output tables (index -> string)
        "onset_out": ["g","kk","n","d","tt","r","m","b","pp","s","ss","","j","jj","ch","k","t","p","h"],
        "vowel_out": ["a","ae","ya","yae","eo","e","yeo","ye","o","wa","wae","oe","yo","u","wo","we","wi","yu","eu","ui","i"],
        # RR coda output uses neutralized letters; we keep a reversible variant by using distinct strings
        "coda_out": ["","k","kk","ks","n","nj","nh","t","l","lk","lm","lb","ls","lt","lp","lh","m","p","ps","t","t","ng","t","t","k","t","p","t"],
    },

    "mr": {
        "name": "McCune–Reischauer",
        "abbr": "MR",
        "year": 1939,
        "notes": "Reversible transliteration variant; uses diacritics ŏ/ŭ and apostrophes for aspiration.",
        "onset": {
            "": 11,
            "k": 0, "kk": 1, "n": 2, "t": 3, "tt": 4, "r": 5, "m": 6,
            "p": 7, "pp": 8, "s": 9, "ss": 10, "ch": 12, "tch": 13, "ch'": 14,
            "k'": 15, "t'": 16, "p'": 17, "h": 18,
        },
        "vowel": {
            "a": 0, "ae": 1, "ya": 2, "yae": 3, "ŏ": 4, "e": 5, "yŏ": 6, "ye": 7,
            "o": 8, "wa": 9, "wae": 10, "oe": 11, "yo": 12,
            "u": 13, "wŏ": 14, "we": 15, "wi": 16, "yu": 17,
            "ŭ": 18, "ŭi": 19, "i": 20,
        },
        "coda": {
            "": 0,
            "k": 1, "kk": 2, "ks": 3, "n": 4, "nj": 5, "nh": 6, "t": 7,
            "l": 8, "lk": 9, "lm": 10, "lb": 11, "ls": 12, "lt": 13, "lp": 14, "lh": 15,
            "m": 16, "p": 17, "ps": 18, "t_s": 19, "t_ss": 20, "ng": 21,
            "t_j": 22, "t_ch": 23, "k_kh": 24, "t_th": 25, "p_ph": 26, "t_h": 27,
        },
        "onset_out": ["k","kk","n","t","tt","r","m","p","pp","s","ss","","ch","tch","ch'","k'","t'","p'","h"],
        "vowel_out": ["a","ae","ya","yae","ŏ","e","yŏ","ye","o","wa","wae","oe","yo","u","wŏ","we","wi","yu","ŭ","ŭi","i"],
        "coda_out": ["","k","k","ks","n","nj","nh","t","l","lk","lm","lb","ls","lt","lp","lh","m","p","ps","t","t","ng","t","t","k","t","p","t"],
    },

    "yale": {
        "name": "Yale romanization of Korean",
        "abbr": "Yale",
        "year": 1942,
        "notes": "Morphophonemic-focused; reversible transliteration variant.",
        "onset": {
            "": 11,
            "k": 0, "kk": 1, "n": 2, "t": 3, "tt": 4, "l": 5, "m": 6,
            "p": 7, "pp": 8, "s": 9, "ss": 10, "c": 12, "cc": 13, "ch": 14,
            "kh": 15, "th": 16, "ph": 17, "h": 18,
        },
        # Yale vowel spellings (modern Korean)
        "vowel": {
            "a": 0, "ay": 1, "ya": 2, "yay": 3, "e": 4, "ey": 5, "ye": 6, "yey": 7,
            "o": 8, "wa": 9, "way": 10, "oy": 11, "yo": 12,
            "u": 13, "we": 14, "wey": 15, "wuy": 16, "yu": 17,
            "u_": 18, "uy": 19, "i": 20,
        },
        "coda": {  # we keep RR-like unique codas for reversibility
            "": 0,
            "k": 1, "kk": 2, "ks": 3, "n": 4, "nc": 5, "nh": 6, "t": 7,
            "l": 8, "lk": 9, "lm": 10, "lp": 11, "ls": 12, "lt": 13, "lp2": 14, "lh": 15,
            "m": 16, "p": 17, "ps": 18, "t_s": 19, "ss": 20, "ng": 21,
            "c": 22, "ch": 23, "kh": 24, "th": 25, "ph": 26, "h": 27,
        },
        "onset_out": ["k","kk","n","t","tt","l","m","p","pp","s","ss","","c","cc","ch","kh","th","ph","h"],
        # For ㅡ we use "u_" (common ASCII-safe stand-in for Yale's special symbol)
        "vowel_out": ["a","ay","ya","yay","e","ey","ye","yey","o","wa","way","oy","yo","u","we","wey","wuy","yu","u_","uy","i"],
        "coda_out": ["","k","kk","ks","n","nc","nh","t","l","lk","lm","lp","ls","lt","lp","lh","m","p","ps","t","ss","ng","c","ch","kh","th","ph","h"],
    },

    # MR-derived variants (kept as aliases for reversible transliteration here)
    "nk1992": {
        "name": "Romanization of Korean (North Korea)",
        "abbr": "NK (1992)",
        "year": 1992,
        "notes": "Includes an 'official' variant based on MR-derived DPRK rules; reversible variant available.",
        # Reversible tables (MR-like with DPRK vowel choices; used for round-trip with syllable_sep)
        "onset": {
            "": 11,
            "k": 0, "kk": 1, "n": 2, "t": 3, "tt": 4, "r": 5, "m": 6,
            "p": 7, "pp": 8, "s": 9, "ss": 10, "ch": 12, "tch": 13, "ch'": 14,
            "k'": 15, "t'": 16, "p'": 17, "h": 18,
        },
        "vowel": {
            "a": 0, "ae": 1, "ya": 2, "yae": 3, "ŏ": 4, "e": 5, "yŏ": 6, "ye": 7,
            "o": 8, "wa": 9, "wae": 10,
            # DPRK often uses "oe" for ㅚ (some sources note later preference for "oi");
            # reversible variant uses "oe".
            "oe": 11,
            "yo": 12,
            "u": 13, "wŏ": 14, "we": 15, "wi": 16, "yu": 17,
            "ŭ": 18, "ŭi": 19, "i": 20,
        },
        "coda": {
            "": 0,
            "k": 1, "kk": 2, "ks": 3, "n": 4, "nj": 5, "nh": 6, "t": 7,
            "l": 8, "lk": 9, "lm": 10, "lb": 11, "ls": 12, "lt": 13, "lp": 14, "lh": 15,
            "m": 16, "p": 17, "ps": 18, "t_s": 19, "t_ss": 20, "ng": 21,
            "t_j": 22, "t_ch": 23, "k_kh": 24, "t_th": 25, "p_ph": 26, "t_h": 27,
        },
        "onset_out": ["k","kk","n","t","tt","r","m","p","pp","s","ss","","ch","tch","ch'","k'","t'","p'","h"],
        "vowel_out": ["a","ae","ya","yae","ŏ","e","yŏ","ye","o","wa","wae","oe","yo","u","wŏ","we","wi","yu","ŭ","ŭi","i"],
        "coda_out": ["","k","k","ks","n","nj","nh","t","l","lk","lm","lb","ls","lt","lp","lh","m","p","ps","t","t","ng","t","t","k","t","p","t"],
    },
    "ala-lc": {
        "name": "ALA-LC romanization for Korean",
        "abbr": "ALA-LC",
        "year": 2009,
        "notes": "Includes an 'official' variant using letter-position rules from the 2009 table; reversible variant available.",
        # Reversible tables (MR-like)
        "onset": {
            "": 11,
            "k": 0, "kk": 1, "n": 2, "t": 3, "tt": 4, "r": 5, "m": 6,
            "p": 7, "pp": 8, "s": 9, "ss": 10, "ch": 12, "tch": 13, "ch'": 14,
            "k'": 15, "t'": 16, "p'": 17, "h": 18,
        },
        "vowel": {
            "a": 0, "ae": 1, "ya": 2, "yae": 3, "ŏ": 4, "e": 5, "yŏ": 6, "ye": 7,
            "o": 8, "wa": 9, "wae": 10, "oe": 11, "yo": 12,
            "u": 13, "wŏ": 14, "we": 15, "wi": 16, "yu": 17,
            "ŭ": 18, "ŭi": 19, "i": 20,
        },
        "coda": {
            "": 0,
            "k": 1, "kk": 2, "ks": 3, "n": 4, "nj": 5, "nh": 6, "t": 7,
            "l": 8, "lk": 9, "lm": 10, "lb": 11, "ls": 12, "lt": 13, "lp": 14, "lh": 15,
            "m": 16, "p": 17, "ps": 18, "t_s": 19, "t_ss": 20, "ng": 21,
            "t_j": 22, "t_ch": 23, "k_kh": 24, "t_th": 25, "p_ph": 26, "t_h": 27,
        },
        "onset_out": ["k","kk","n","t","tt","r","m","p","pp","s","ss","","ch","tch","ch'","k'","t'","p'","h"],
        "vowel_out": ["a","ae","ya","yae","ŏ","e","yŏ","ye","o","wa","wae","oe","yo","u","wŏ","we","wi","yu","ŭ","ŭi","i"],
        "coda_out": ["","k","k","ks","n","nj","nh","t","l","lk","lm","lb","ls","lt","lp","lh","m","p","ps","t","t","ng","t","t","k","t","p","t"],
    },
}

def _kroman_resolve_system(system: str) -> dict[str, object]:
    key = system.strip().lower()
    sysd = KROMAN_SYSTEMS.get(key)
    if sysd is None:
        sysd = KROMAN_SYSTEMS["rr"]
    # resolve aliases
    if "alias_of" in sysd:
        sysd = KROMAN_SYSTEMS[str(sysd["alias_of"])]
    return sysd


def _compose_hangul(L: int, V: int, T: int) -> str:
    return chr(_HANGUL_BASE + ((L * _NUM_VOWELS + V) * _NUM_TAILS) + T)




# ----------------------------
# Official encoders (ALA-LC 2009/2025 table; DPRK MR-for-DPRK guidance)
# ----------------------------
#
# These implement **letter-position** behavior (context-sensitive) based on:
# - Library of Congress "Korean Romanization Table (2009 version)" (minor layout fixes July 2025)
#   Letter Position Rules for Romanization (pp. 64-67 in the PDF).  citeturn1view0
# - NGA "ROMANIZATION OF KOREAN - MR for DPRK" guidance tables (2017). citeturn3view0
#
# Important: These are "official-ish" pragmatic implementations. ALA-LC also specifies
# word-division and many dictionary-based pronunciation exceptions; DPRK guidance includes
# large consonant cluster tables. We implement the most impactful *within-word* letter-position
# rules so output looks like the official tables for common cases. For perfect reversibility, use
# variant="reversible" (the dict-based syllable tables).

# Choseong and Jongseong inventories (standard Unicode order)
_CHO = ["ㄱ","ㄲ","ㄴ","ㄷ","ㄸ","ㄹ","ㅁ","ㅂ","ㅃ","ㅅ","ㅆ","ㅇ","ㅈ","ㅉ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]
_JONG = ["","ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ","ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"]

# Vowel sets used in ALA-LC rules
# yotized vowels: ㅑ ㅒ ㅕ ㅖ ㅛ ㅠ  (Unicode jungseong indices: 2,3,6,7,12,17)
_VOWELS_YOTIZED = {2, 3, 6, 7, 12, 17}
# 'wi' vowel (ㅟ) index is 16 in Unicode jungseong order
_VOWEL_WI = 16
# ㅣ index is 20
_VOWEL_I = 20

# Helper: detect "word boundary" for official rules
def _is_word_boundary(prev_char: str | None) -> bool:
    return prev_char is None or not _is_hangul_syllable(prev_char)

# Word-boundary logic for "official" romanization:
# - boundary_mode="whitespace": boundaries only on whitespace
# - boundary_mode="whitespace_punct": whitespace and most punctuation reset word-initial rules
# - boundary_mode="custom": use `boundary_chars` as the reset set
#
# We avoid treating '.' and ',' as word boundaries when they are between digits (e.g., 3.14, 1,000).

_DEFAULT_PUNCT_RESET = ".,;:!?()[]{}<>\"'“”‘’/\\|·•—–-"
_WHITESPACE = " \\t\\n\\r\\f\\v"

def _boundary_reset_set(boundary_mode: str, boundary_chars: str | None) -> set[str]:
    mode = (boundary_mode or "whitespace_punct").lower()
    if mode == "whitespace":
        return set(_WHITESPACE)
    if mode == "custom":
        return set(boundary_chars or "")
    return set(_WHITESPACE) | set(_DEFAULT_PUNCT_RESET)

def _sep_resets_word(sep_text: str, prev_char: str | None, next_char: str | None, reset_set: set[str]) -> bool:
    if any(ch in _WHITESPACE for ch in sep_text):
        return True
    if sep_text in {".", ","} and (prev_char and prev_char.isdigit()) and (next_char and next_char.isdigit()):
        return False
    return any(ch in reset_set for ch in sep_text)

def _apply_word_sep_policy(sep_text: str, policy: str) -> str:
    """Normalize separator output.

    Policies:
    - keep: return original separator text
    - space: replace any separator run with single space
    - hyphenate: pure-whitespace runs become '-', but mixed punctuation+whitespace keeps punctuation and normalizes whitespace to single spaces
    - smart: normalize whitespace to single spaces, keep punctuation/order (retains a space around punctuation if it was there)
    - smart_hyphenate: like smart, but pure-whitespace runs become '-'

    This avoids smashing things like "대한 (민국)" into "대한(민국)".
    """
    policy = (policy or "keep").lower()
    if policy == "keep":
        return sep_text

    # Normalize any whitespace run to a single space (preserving punctuation and order)
    norm_ws = re.sub(r"[ \\t\\n\\r\\f\\v]+", " ", sep_text)

    # Pure whitespace separator?
    is_pure_ws = (norm_ws.strip() == "") and any(ch in _WHITESPACE for ch in sep_text)

    if policy == "space":
        return " "

    if policy == "hyphenate":
        return "-" if is_pure_ws else norm_ws

    if policy == "smart":
        return " " if is_pure_ws else norm_ws

    if policy == "smart_hyphenate":
        return "-" if is_pure_ws else norm_ws

    return sep_text

def _ala_initial_n_r_suppressed(L: int, V: int) -> bool:
    # ALA-LC: initial ㄴ, ㄹ not romanized before ㅣ and yotized vowels (Letter Position Rules table). citeturn1view0
    return (V == _VOWEL_I) or (V in _VOWELS_YOTIZED)


def _ala_onset(L: int, V: int, prev_T: int | None, prev_is_hangul: bool, prev_T_is_vowel: bool, next_L: int | None) -> str:
    """ALA-LC onset (syllabic initial) with letter-position rules."""
    # ㅇ onset: not romanized
    if L == _L_IEUNG_INDEX:
        return ""

    # Word-initial ㄴ / ㄹ suppression
    if prev_is_hangul is False:
        if L in (2, 5) and _ala_initial_n_r_suppressed(L, V):
            return ""
        # initial ㄹ -> n before other vowels per table. citeturn1view0
        if L == 5:
            return "n"
        # initial ㄴ -> n (handled above when suppressed)
        if L == 2:
            return "n"
        # other initials: fixed forms (table uses apostrophes for aspiration)
        return ["k","kk","n","t","tt","r","m","p","pp","s","ss","","ch","tch","ch'","k'","t'","p'","h"][L]

    # Medial onset rules (within a word)
    prev_jong = _JONG[prev_T or 0]
    prev_coda_jamo = prev_jong

    # ㄴ: L when preceded or followed by ㄹ, else n citeturn1view0
    if L == 2:
        if prev_coda_jamo == "ㄹ" or (next_L is not None and _CHO[next_L] == "ㄹ"):
            return "l"
        return "n"

    # ㄹ medial: r between vowels or before ㅎ; l before other consonants or after ㄴ and ㄹ; n after other consonants citeturn1view0
    if L == 5:
        if prev_T_is_vowel:  # between vowels
            return "r"
        if next_L is not None and _CHO[next_L] == "ㅎ":
            return "r"
        if prev_coda_jamo in ("ㄴ", "ㄹ"):
            return "l"
        # before other consonants
        if next_L is not None and _CHO[next_L] != "ㅇ":
            return "l"
        # after other consonants
        return "n"

    # ㄱ medial onset: g between vowels or after ㄴㄹㅁㅇ; k after other consonants citeturn1view0
    if L == 0:
        if prev_T_is_vowel:
            return "g"
        if prev_coda_jamo in ("ㄴ", "ㄹ", "ㅁ", "ㅇ"):
            return "g"
        return "k"

    # ㄷ medial onset: d between vowels or after ㄴㅁㅇ; t after ㄱㅂㄹㅅ citeturn1view0
    if L == 3:
        if prev_T_is_vowel:
            return "d"
        if prev_coda_jamo in ("ㄴ", "ㅁ", "ㅇ"):
            return "d"
        if prev_coda_jamo in ("ㄱ", "ㅂ", "ㄹ", "ㅅ"):
            return "t"
        return "d"

    # ㅂ medial onset: b between vowels or after ㄴㄹㅁㅇ; m before ㄴㄹㅁ; p otherwise citeturn1view0
    if L == 7:
        if next_L is not None and _CHO[next_L] in ("ㄴ","ㄹ","ㅁ"):
            return "m"
        if prev_T_is_vowel:
            return "b"
        if prev_coda_jamo in ("ㄴ","ㄹ","ㅁ","ㅇ"):
            return "b"
        return "p"

    # ㅅ onset: sh before ㅟ, else s citeturn1view0
    if L == 9:
        return "sh" if V == _VOWEL_WI else "s"

    # ㅈ medial onset: j between vowels or after ㄴㅁㅇ; ch after other consonants citeturn1view0
    if L == 12:
        if prev_T_is_vowel:
            return "j"
        if prev_coda_jamo in ("ㄴ","ㅁ","ㅇ"):
            return "j"
        return "ch"

    # ㅊ onset: always ch' as syllabic initial citeturn1view0
    if L == 14:
        return "ch'"

    # ㅋ onset: always k'
    if L == 15:
        return "k'"

    # ㅌ onset: t' generally; t after ㄱㄷㅅㅈ when consonant-following rule applies citeturn1view0
    if L == 16:
        if prev_coda_jamo in ("ㄱ","ㄷ","ㅅ","ㅈ"):
            return "t"
        return "t'"

    # ㅍ onset: always p' as syllabic initial
    if L == 17:
        return "p'"

    # ㅎ onset: h after ㄱㅂㅅ; ch' after ㄷㅈ; else h citeturn1view0
    if L == 18:
        if prev_coda_jamo in ("ㄱ","ㅂ","ㅅ"):
            return "h"
        if prev_coda_jamo in ("ㄷ","ㅈ"):
            return "ch'"
        return "h"

    # Tense consonants: ㄲ/ㄸ/ㅃ/ㅆ/ㅉ fixed
    if L == 1:  # ㄲ
        return "kk"
    if L == 4:  # ㄸ
        return "tt"
    if L == 8:  # ㅃ
        return "pp"
    if L == 10:  # ㅆ
        return "ss"
    if L == 13:  # ㅉ
        return "tch"

    # fallback (shouldn't happen)
    return ["k","kk","n","t","tt","r","m","p","pp","s","ss","","ch","tch","ch'","k'","t'","p'","h"][L]


def _ala_coda(T: int, next_L: int | None, next_V: int | None, next_is_hangul: bool) -> str:
    """ALA-LC coda (syllabic final) with letter-position rules + double-final consonant rules.

    Implements:
    - Letter Position Rules (Appendix 7, pp. 64-67). citeturn1view0
    - Double consonants / final clusters rules (sections around pp. 10-13). citeturn1view0

    Notes:
    - Some exceptions (밟-, 넓-) are implemented in a minimal, pattern-based way.
    - For perfect reversibility, use variant="reversible".
    """
    if T == 0:
        return ""

    jong = _JONG[T]

    # Determine next onset jamo and whether next begins with a vowel (i.e., next onset is ㅇ)
    next_cho = _CHO[next_L or _L_IEUNG_INDEX] if next_is_hangul else None
    next_is_vowel = bool(next_is_hangul and next_cho == "ㅇ")

    # ---- Special rules for ㅎ/ㄶ/ㅀ before vowels (section near p. 9-10). citeturn1view0
    if jong == "ㅎ" and next_is_vowel:
        return ""  # do not romanize
    if jong == "ㄶ" and next_is_vowel:
        return "n"
    if jong == "ㅀ" and next_is_vowel:
        return "r"

    # ㅀ followed by ㄴ => ll (p. 9). citeturn1view0
    if jong == "ㅀ" and next_cho == "ㄴ":
        return "ll"

    # ---- Double final consonants (clusters) rules (pp. 10-13). citeturn1view0

    # (a) Word-final clusters (or before non-hangul): romanize as pronounced
    if not next_is_hangul:
        # ㄳ, ㄺ -> k; ㄻ -> m; ㄼ, ㄽ -> l; ㅄ -> p (p. 10). citeturn1view0
        if jong in ("ㄳ", "ㄺ"):
            return "k"
        if jong == "ㄻ":
            return "m"
        if jong in ("ㄼ", "ㄽ"):
            return "l"
        if jong == "ㅄ":
            return "p"
        # fallback
        return KROMAN_SYSTEMS["ala-lc"]["coda_out"][T]  # type: ignore[index]

    # (c) Followed by vowels: explicit cluster romanizations (p. 12). citeturn1view0
    if next_is_vowel:
        if jong == "ㄵ":
            return "nj"
        if jong == "ㄺ":
            return "lg"
        if jong == "ㄻ":
            return "lm"
        if jong == "ㄼ":
            return "lb"
        if jong == "ㄾ":
            return "lt'"
        if jong == "ㄿ":
            return "lp'"
        if jong == "ㅄ":
            return "ps"
        if jong == "ㅆ":
            return "ss"
        # ㅎ/ㄶ/ㅀ already handled above
        return KROMAN_SYSTEMS["ala-lc"]["coda_out"][T]  # type: ignore[index]

    # (b) Followed by other consonants: cluster-specific rules (p. 10-11). citeturn1view0
    if jong == "ㄲ":
        return "k"
    if jong == "ㄺ":
        if next_cho == "ㄱ":
            return "l"
        if next_cho == "ㄴ":
            return "ng"
        return "k"
    if jong == "ㄻ":
        return "m"
    if jong == "ㄵ":
        return "n"
    if jong in ("ㄼ", "ㄽ", "ㄾ"):
        # Exception 1: 밟- => m before ㄴ, else p (p. 11). citeturn1view0
        # We can't fully detect stems; this catches the exact syllable 밟.
        # Handled outside this function in the caller if needed; here we implement generally:
        return "l"
    if jong in ("ㅄ", "ㄿ"):
        # Exception 1 for 밟- will override in caller when detected.
        return "p"
    if jong == "ㅆ":
        return "n" if next_cho == "ㄴ" else "t"

    # Now apply the core ALA-LC *single final* letter-position rules for key finals (Appendix 7). citeturn1view0
    if jong == "ㄱ":
        return "ng" if next_cho in ("ㄴ", "ㄹ", "ㅁ") else "k"
    if jong == "ㄷ":
        return "n" if next_cho == "ㄴ" else "t"
    if jong == "ㅂ":
        return "m" if next_cho in ("ㄴ", "ㄹ", "ㅁ") else "p"
    if jong == "ㅈ":
        return "n" if next_cho in ("ㄴ", "ㅁ") else "t"
    if jong == "ㅊ":
        if next_cho == "ㅇ":
            return "j"
        return "n" if next_cho in ("ㄴ", "ㅁ") else "t"
    if jong == "ㅅ":
        if next_cho in ("ㄴ", "ㅁ"):
            return "n"
        if next_cho in ("ㄱ", "ㄷ", "ㅂ", "ㅅ", "ㅈ", "ㅎ"):
            return "t"
        return "s"
    if jong == "ㅎ":
        if next_cho == "ㅇ":
            return ""
        if next_cho == "ㄴ":
            return "nn"
        return "t"
    if jong == "ㄲ":
        return "kk" if next_cho == "ㅇ" else "k"

    return KROMAN_SYSTEMS["ala-lc"]["coda_out"][T]  # type: ignore[index]

    next_cho = _CHO[next_L or _L_IEUNG_INDEX]

    # ㄱ: NG before ㄴㄹㅁ; otherwise K citeturn1view0
    if jong == "ㄱ":
        return "ng" if next_cho in ("ㄴ","ㄹ","ㅁ") else "k"

    # ㄷ: N before ㄴ, else T citeturn1view0
    if jong == "ㄷ":
        return "n" if next_cho == "ㄴ" else "t"

    # ㅂ: M before ㄴㄹㅁ; else P citeturn1view0
    if jong == "ㅂ":
        return "m" if next_cho in ("ㄴ","ㄹ","ㅁ") else "p"

    # ㅈ: N before ㄴㅁ; else T citeturn1view0
    if jong == "ㅈ":
        return "n" if next_cho in ("ㄴ","ㅁ") else "t"

    # ㅊ: J before vowels (i.e., next onset ㅇ), N before ㄴㅁ, else T citeturn1view0
    if jong == "ㅊ":
        if next_cho == "ㅇ":
            return "j"
        return "n" if next_cho in ("ㄴ","ㅁ") else "t"

    # ㅅ: N before ㄴㅁ; T before ㄱㄷㅂㅅㅈ; otherwise S before vowels/others. citeturn2view0
    if jong == "ㅅ":
        if next_cho in ("ㄴ","ㅁ"):
            return "n"
        if next_cho in ("ㄱ","ㄷ","ㅂ","ㅅ","ㅈ","ㅎ"):
            return "t"
        # before vowels: s
        return "s"

    # ㅆ: N before ㄴ; else T citeturn1view0
    if jong == "ㅆ":
        return "n" if next_cho == "ㄴ" else "t"

    # ㅎ: not romanized as syllabic final before vowels; NN before ㄴ; else T citeturn1view0
    if jong == "ㅎ":
        if next_cho == "ㅇ":
            return ""
        if next_cho == "ㄴ":
            return "nn"
        return "t"

    # ㄲ: KK before vowels; K otherwise citeturn1view0
    if jong == "ㄲ":
        return "kk" if next_cho == "ㅇ" else "k"

    # For clusters and other finals, fall back to reversible coda_out (MR-like) which is close to ALA-LC examples.
    return KROMAN_SYSTEMS["ala-lc"]["coda_out"][T]  # type: ignore[index]


def _nk1992_onset(L: int, V: int, word_initial: bool) -> str:
    """DPRK MR-for-DPRK onset, simplified from NGA tables. citeturn3view0"""
    if L == _L_IEUNG_INDEX:
        return ""

    # Initial ㄴ may be not romanized before i/yotized; simplified like ALA-LC. citeturn3view0
    if word_initial and L == 2 and (V == _VOWEL_I or V in _VOWELS_YOTIZED):
        return ""
    # Initial ㄹ may be not romanized before i/yotized; otherwise often n at beginning-of-word in DPRK table.
    if word_initial and L == 5:
        if V == _VOWEL_I or V in _VOWELS_YOTIZED:
            return ""
        return "n"

    base = ["k","kk","n","t","tt","r","m","p","pp","s","ss","","ch","tch","ch'","k'","t'","p'","h"]
    return base[L]


def _nk1992_coda(T: int, next_is_hangul: bool) -> str:
    """DPRK MR-for-DPRK coda, simplified from NGA table 1 (end of word). citeturn3view0"""
    if T == 0:
        return ""
    jong = _JONG[T]
    # End-of-word ㅎ is not romanized (table 1)
    if jong == "ㅎ" and not next_is_hangul:
        return ""
    # otherwise MR-like
    return KROMAN_SYSTEMS["nk1992"]["coda_out"][T]  # type: ignore[index]


# Full Table 3 (word-medial consonant cluster romanizations) and Table 4 (irregular CV forms)
# from the MR-for-DPRK reference. citeturn3view0
#
# We embed the tables in a compact, parseable form. The parser builds a mapping that can be used
# to rewrite the boundary between syllables (previous coda / next onset) to match Table 3, and
# to override certain onset+vowel combinations per Table 4.

_NK_TABLE3_INITIALS = ["ᄀ","ᄂ","ᄃ","ᄅ","ᄆ","ᄇ","ᄉ","ᄋ","ᄌ","ᄎ","ᄏ","ᄐ","ᄑ","ᄒ","ᄁ","ᄄ","ᄈ","ᄊ","ᄍ"]

_NK_TABLE3_ROWS: list[tuple[str, list[str]]] = [
    ("ᄀ", "kk ngn kt ngn ngm kp ks g kch kch' kk' kt' kp' kh kk ktt kpp kss ktch".split()),
    ("ᄂ", "n'g nn nd ll nm nb ns n nj nch' nk' nt' np' nh nkk ntt npp nss ntch".split()),
    ("ᄃ", "kk nn tt nn nm pp ss d tch tch' tk' tt' tp' th tkk tt tpp tss tch".split()),
    ("ᄅ", "lg ll lt ll lm lb ls r lch lch' lk' lt' lp' rh lkk ltt lpp lss ltch".split()),
    ("ᄆ", "mg mn md mn mm mb ms m mj mch' mk' mt' mp' mh mkk mtt mpp mss mtch".split()),
    ("ᄇ", "pk mn pt mn mm pp ps b pch pch' pk' pt' pp' ph pkk ptt pp pss ptch".split()),
    ("ᄉ", "kk nn tt nn nm pp ss d tch tch' tk' tt' tp' th tkk tt tpp ss tch".split()),
    ("ᄋ", "ngg ngn ngd ngn ngm ngb ngs ng ngj ngch' ngk' ngt' mgp' ng ngkk ngtt ngpp ngss ngtch".split()),
    ("vowel", "g n d r m b s j ch' k' t' p' h kk tt pp ss tch".split()),
    ("ᄌ", "kk nn tt nn nm pp ss d tch tch' tk' tt' tp' th tkk tt tpp ss tch".split()),
    ("ᄎ", "kk nn tt nn nm pp ss d tch tch' tk' tt' tp' th tkk tt tpp ss tch".split()),
    ("ᄏ", "kk ngn kt ngn ngm kp ks k kch kcch' kk' kt' kp' kh kk ktt kpp kss ktch".split()),
    ("ᄐ", "kk nn tt nn nm pp ss d tch tch' tk' tt' tp' tk tkk tt tpp ss tch".split()),
    ("ᆰ", "lg ngn kt ngl ngm kp ks lg kch kch' lk' kt' kp' lkh lkk kt kpp kss ktch".split()),
    ("ᆱ", "mg mn md ml lm mb ms lm mj mch' mk' mt' mp' mh mkk mtt mpp mss mtch".split()),
    ("ᆲ", "pk mn pt ml mm lb ps lb pch pch' pk' pt' lp' lph pkk ptt lpp pss ptch".split()),
    ("ᆬ", "nk nn nt nl nm nb ns nj nj nch' nk' nt' np' nh nkk ntt npp nss ntch".split()),
    ("ᆭ", "nk nn nt nl nm nb ns nh nj nch' nk' nt' np' nh nkk ntt npp nss ntch".split()),
    ("ㅄ", "pk pn pt pl pm pp ps ps pj pch' pk' pt' pp' ph pkk ptt pp pss ptch".split()),
    ("ㄲ", "kk ngn kt ngn ngm kp ks g kch kch' kk' kt' kp' kh kk ktt kpp kss ktch".split()),
    ("ㅆ", "kk nn tt nn nm pp ss s tch tch' tk' tt' tp' th tkk tt tpp tss tch".split()),
    ("ㅍ", "pk mn pt mn mm pp ps p pch pch' pk' pt' pp' ph pkk ptt pp pss ptch".split()),
    ("ㅎ", "k' n t' r m p' s h ch' ch' k' t' p' h kk tt pp ss tch".split()),
    ("ㅀ", "lk' ll lt' ll lm lp' ls rh lch' lch' lk' lt' lp' rh lkk ltt lpp lss ltch".split()),
]

_NK_TABLE4_OVERRIDES: dict[tuple[str, int, bool], str] = {
    ("ᄀ", 20, True): "ki",
    ("ᄀ", 20, False): "gi",
    ("ᄂ", 2, True): "ya", ("ᄂ", 6, True): "yŏ", ("ᄂ", 12, True): "yo", ("ᄂ", 17, True): "yu",
    ("ᄂ", 20, True): "i", ("ᄂ", 7, True): "ye",
    ("ᄂ", 2, False): "nya", ("ᄂ", 6, False): "nyŏ", ("ᄂ", 12, False): "nyo", ("ᄂ", 17, False): "nyu",
    ("ᄂ", 20, False): "ni", ("ᄂ", 7, False): "nye",
    ("ᄃ", 20, True): "ti", ("ᄃ", 20, False): "di",
    ("ᄌ", 20, True): "chi", ("ᄌ", 20, False): "ji",
    ("ᄉ", 16, True): "shwi", ("ᄉ", 16, False): "shwi",
}

def _nk_build_table3_boundary_map() -> dict[tuple[str, str], tuple[str, str]]:
    onset_for: dict[str, str] = {
        "ᄀ": "g", "ᄂ": "n", "ᄃ": "d", "ᄅ": "r", "ᄆ": "m", "ᄇ": "b", "ᄉ": "s", "ᄋ": "",
        "ᄌ": "j", "ᄎ": "ch'", "ᄏ": "k'", "ᄐ": "t'", "ᄑ": "p'", "ᄒ": "h",
        "ᄁ": "kk", "ᄄ": "tt", "ᄈ": "pp", "ᄊ": "ss", "ᄍ": "tch",
    }
    boundary: dict[tuple[str, str], tuple[str, str]] = {}
    for final_j, cells in _NK_TABLE3_ROWS:
        cells = (cells + [""] * 19)[:19]
        for init_j, cluster in zip(_NK_TABLE3_INITIALS, cells):
            if not cluster:
                continue
            onset = onset_for.get(init_j, "")
            prev_part = cluster
            next_part = onset
            if onset and cluster.endswith(onset):
                prev_part = cluster[: -len(onset)]
                next_part = onset
            else:
                for cand in sorted(set(onset_for.values()), key=len, reverse=True):
                    if cand and cluster.endswith(cand):
                        prev_part = cluster[: -len(cand)]
                        next_part = cand
                        break
            boundary[(final_j, init_j)] = (prev_part, next_part)
    return boundary

_NK_TABLE3_BOUNDARY_MAP = _nk_build_table3_boundary_map()


def _hangul_to_kroman_official(text: str, system: str, syllable_sep: str = "-", *, split_words: bool = False, word_sep_policy: str = "keep", boundary_mode: str = "whitespace_punct", boundary_chars: str | None = None) -> str:
    """Apply official-ish letter-position rules for ALA-LC or DPRK (1992).

    This function is context-sensitive across syllable boundaries in a *best-effort* way.
    """
    sys_key = system.lower().strip()
    sysd = _kroman_resolve_system(sys_key)
    vowel_out = sysd["vowel_out"]  # type: ignore[assignment]
    if split_words:
        reset_set = _boundary_reset_set(boundary_mode, boundary_chars)
        out_chunks: list[str] = []
        i0 = 0
        n0 = len(text)
        while i0 < n0:
            if _is_hangul_syllable(text[i0]):
                j0 = i0 + 1
                while j0 < n0 and _is_hangul_syllable(text[j0]):
                    j0 += 1
                out_chunks.append(_hangul_to_kroman_official(text[i0:j0], system, syllable_sep=syllable_sep, split_words=False))
                i0 = j0
            else:
                j0 = i0 + 1
                while j0 < n0 and not _is_hangul_syllable(text[j0]):
                    j0 += 1
                sep = text[i0:j0]
                prev_c = text[i0 - 1] if i0 > 0 else None
                next_c = text[j0] if j0 < n0 else None

                out_chunks.append(_apply_word_sep_policy(sep, word_sep_policy))

                if not _sep_resets_word(sep, prev_c, next_c, reset_set):
                    if j0 < n0 and _is_hangul_syllable(text[j0]):
                        k0 = j0 + 1
                        while k0 < n0 and _is_hangul_syllable(text[k0]):
                            k0 += 1
                        out_chunks.append(_hangul_to_kroman_official(text[j0:k0], system, syllable_sep=syllable_sep, split_words=False))
                        i0 = k0
                        continue

                i0 = j0
        return "".join(out_chunks)

    chars = list(text)
    decomp = [_decompose_hangul(ch) for ch in chars]

    out_parts: list[str] = []

    for i, d in enumerate(decomp):
        if d is None:
            out_parts.append(chars[i])
            continue

        L, V, T = d

        # Lookahead to next hangul syllable
        next_d = decomp[i + 1] if i + 1 < len(decomp) else None
        next_is_hangul = next_d is not None
        next_L = next_d[0] if next_d else None
        next_V = next_d[1] if next_d else None

        prev_ch = chars[i - 1] if i > 0 else None
        prev_d = decomp[i - 1] if i > 0 else None
        prev_is_hangul = prev_d is not None
        prev_T = prev_d[2] if prev_d else None
        prev_T_is_vowel = (prev_T == 0) if prev_T is not None else True

        if sys_key == "ala-lc":
            # Onset depends on previous syllable coda and next onset in some cases
            onset = _ala_onset(L, V, prev_T, prev_is_hangul, prev_T_is_vowel, next_L)
            coda = _ala_coda(T, next_L, next_V, next_is_hangul)
            # Exceptions from Double Consonants section (p. 11). citeturn1view0
            # 밟- : romanize as m before ㄴ, else p
            if chars[i] == "밟" and next_is_hangul:
                nxt = _CHO[next_L or _L_IEUNG_INDEX]
                coda = "m" if nxt == "ㄴ" else "p"
            # 넓- : romanize as p in certain lexemes (examples: 넓죽하다/넓둥글다/넓적)
            if chars[i] == "넓" and next_is_hangul:
                nxt = _CHO[next_L or _L_IEUNG_INDEX]
                if nxt in ("ㅈ", "ㄷ", "ㅊ"):
                    coda = "p"

            out_parts.append(onset + vowel_out[V] + coda)

        else:

            # DPRK onset rules with Table 4 (irregular CV) + Table 3 (boundary clusters). citeturn3view0

            word_initial = (not prev_is_hangul) or (split_words and _is_word_boundary_char(prev_ch))


            # Map compat choseong to leading jamo key used in tables

            compat_to_lead = {

                "ㄱ":"ᄀ","ㄴ":"ᄂ","ㄷ":"ᄃ","ㄹ":"ᄅ","ㅁ":"ᄆ","ㅂ":"ᄇ","ㅅ":"ᄉ","ㅇ":"ᄋ",

                "ㅈ":"ᄌ","ㅊ":"ᄎ","ㅋ":"ᄏ","ㅌ":"ᄐ","ㅍ":"ᄑ","ㅎ":"ᄒ","ㄲ":"ᄁ","ㄸ":"ᄄ",

                "ㅃ":"ᄈ","ㅆ":"ᄊ","ㅉ":"ᄍ",

                # finals/clusters

                "ㄺ":"ᆰ","ㄻ":"ᆱ","ㄼ":"ᆲ","ㄵ":"ᆬ","ㄶ":"ᆭ","ㅄ":"ㅄ","ㅀ":"ㅀ",

            }

            init_key = compat_to_lead.get(_CHO[L], _CHO[L])


            # Table 4: override onset+vowel for certain environments

            ov = _NK_TABLE4_OVERRIDES.get((init_key, V, word_initial))

            if ov is not None:

                onset_vowel = ov

            else:

                onset = _nk1992_onset(L, V, word_initial)

                onset_vowel = onset + vowel_out[V]


            coda = _nk1992_coda(T, next_is_hangul)


            # Table 3: rewrite boundary between previous final and this initial (within Hangul run)

            if prev_is_hangul:

                prev_final = _JONG[prev_T or 0] if prev_T is not None else ""

                prev_key = compat_to_lead.get(prev_final, prev_final)

                key = (prev_key, init_key)

                if key in _NK_TABLE3_BOUNDARY_MAP and out_parts:

                    prev_coda_new, onset_new = _NK_TABLE3_BOUNDARY_MAP[key]

                    old_prev_coda = _nk1992_coda(prev_T or 0, True)

                    if old_prev_coda and out_parts[-1].endswith(old_prev_coda):

                        out_parts[-1] = out_parts[-1][:-len(old_prev_coda)] + prev_coda_new

                    # swap onset in current onset_vowel (keep vowel part)

                    if ov is None:

                        onset_vowel = onset_new + vowel_out[V]

                    else:

                        # ov includes vowel already; preserve its tail by stripping leading letters

                        m2 = re.match(r"([a-zA-Z’']*)(.*)$", ov)

                        if m2:

                            onset_vowel = onset_new + m2.group(2)


            out_parts.append(onset_vowel + coda)

    return syllable_sep.join(out_parts) if syllable_sep else "".join(out_parts)

def hangul_to_kroman_text(text: str, system: str = "rr", syllable_sep: str = "-", variant: str = "reversible", *, split_words: bool = False, word_sep_policy: str = "keep", boundary_mode: str = "whitespace_punct", boundary_chars: str | None = None) -> str:
    """Hangul -> Korean romanization (system aware).

    Parameters
    - system: "rr" | "mr" | "yale" | "ala-lc" | "nk1992"
    - syllable_sep: separator inserted between syllables. Strongly recommended for round-trip.
    - variant:
        - "reversible" (default): syllable-by-syllable transliteration designed to invert perfectly with
          `kroman_to_hangul_text` when using the same `system` and `syllable_sep`.
        - "official": apply system-specific letter-position rules (where available). This is closer to
          published tables but may not be fully reversible without additional markup.

    Note: The "official" variant does not implement all phonological / word-division cataloging rules.
    """
    sys_key = system.strip().lower()
    sysd = _kroman_resolve_system(sys_key)

    if variant.strip().lower() == "official" and sys_key in ("ala-lc", "nk1992"):
        # Official-ish variants are context dependent (neighbors).
        return _hangul_to_kroman_official(text, sys_key, syllable_sep=syllable_sep, split_words=split_words, word_sep_policy=word_sep_policy, boundary_mode=boundary_mode, boundary_chars=boundary_chars)

    onset_out = sysd["onset_out"]  # type: ignore[assignment]
    vowel_out = sysd["vowel_out"]  # type: ignore[assignment]
    coda_out = sysd["coda_out"]    # type: ignore[assignment]

    out: list[str] = []
    for ch in text:
        d = _decompose_hangul(ch)
        if d is None:
            out.append(ch)
            continue
        L, V, T = d
        s = onset_out[L] + vowel_out[V] + coda_out[T]
        out.append(s)

    return syllable_sep.join(out) if syllable_sep else "".join(out)


def kroman_to_hangul_text(text: str, system: str = "rr", syllable_sep: str = "-", variant: str = "reversible") -> str:
    """Korean romanization -> Hangul (system aware).

    This decoder is designed to perfectly invert `hangul_to_kroman_text` when `syllable_sep`
    matches the encoder's separator (default "-"). Without a separator, decoding may be ambiguous.
    """
    sysd = _kroman_resolve_system(system)

    onset_map: dict[str, int] = dict(sysd["onset"])  # type: ignore[arg-type]
    vowel_map: dict[str, int] = dict(sysd["vowel"])  # type: ignore[arg-type]
    coda_map: dict[str, int] = dict(sysd["coda"])    # type: ignore[arg-type]

    # Sort keys for greedy matching
    onset_keys = sorted(onset_map.keys(), key=len, reverse=True)
    vowel_keys = sorted(vowel_map.keys(), key=len, reverse=True)
    coda_keys = sorted(coda_map.keys(), key=len, reverse=True)

    def parse_syllable(token: str) -> str | None:
        t = token
        # onset
        L = None
        onset_len = 0
        for k in onset_keys:
            if k and t.startswith(k):
                L = onset_map[k]
                onset_len = len(k)
                break
        if L is None:
            # try empty onset (ㅇ)
            L = onset_map.get("", _L_IEUNG_INDEX)
            onset_len = 0

        t2 = t[onset_len:]

        # vowel (required)
        V = None
        vlen = 0
        for k in vowel_keys:
            if t2.startswith(k):
                V = vowel_map[k]
                vlen = len(k)
                break
        if V is None:
            return None
        t3 = t2[vlen:]

        # coda (optional) - must match whole remainder
        T = coda_map.get(t3)
        if T is None:
            return None
        return _compose_hangul(L, V, T)

    if syllable_sep:
        parts = text.split(syllable_sep)
        out: list[str] = []
        for part in parts:
            if part == "":
                continue
            syl = parse_syllable(part)
            out.append(syl if syl is not None else part)
        return "".join(out)

    # No separator: greedy scanning (best-effort)
    s = text
    i = 0
    n = len(s)
    out2: list[str] = []
    max_on = max((len(k) for k in onset_keys), default=0)
    max_v = max((len(k) for k in vowel_keys), default=0)
    max_c = max((len(k) for k in coda_keys), default=0)

    while i < n:
        # Try to parse a syllable starting at i by exploring plausible splits.
        matched = None
        for on_len in range(min(max_on, n - i), -1, -1):
            onset_chunk = s[i:i + on_len]
            if on_len == 0:
                if "" not in onset_map:
                    continue
                L = onset_map[""]
            else:
                if onset_chunk not in onset_map:
                    continue
                L = onset_map[onset_chunk]

            j = i + on_len
            # vowel must exist
            for v_len in range(min(max_v, n - j), 1 - 1, -1):
                vow_chunk = s[j:j + v_len]
                if vow_chunk not in vowel_map:
                    continue
                V = vowel_map[vow_chunk]
                k = j + v_len
                # coda is whatever we can match (including empty)
                for c_len in range(min(max_c, n - k), -1, -1):
                    coda_chunk = s[k:k + c_len]
                    if coda_chunk in coda_map:
                        T = coda_map[coda_chunk]
                        matched = (_compose_hangul(L, V, T), k + c_len)
                        break
                if matched:
                    break
            if matched:
                break

        if matched:
            ch, new_i = matched
            out2.append(ch)
            i = new_i
        else:
            out2.append(s[i])
            i += 1

    return "".join(out2)


# ============================================================
# Hangul syllable utilities (for double-vowel mode + katakana ー)
# ============================================================

_HANGUL_BASE = 0xAC00
_HANGUL_LAST = 0xD7A3
_NUM_ONSETS = 19
_NUM_VOWELS = 21
_NUM_TAILS = 28
_L_IEUNG_INDEX = 11  # ㅇ initial


def _is_hangul_syllable(ch: str) -> bool:
    o = ord(ch)
    return _HANGUL_BASE <= o <= _HANGUL_LAST


def _decompose_hangul(ch: str) -> tuple[int, int, int] | None:
    o = ord(ch)
    if not (_HANGUL_BASE <= o <= _HANGUL_LAST):
        return None
    sindex = o - _HANGUL_BASE
    L = sindex // (_NUM_VOWELS * _NUM_TAILS)
    V = (sindex % (_NUM_VOWELS * _NUM_TAILS)) // _NUM_TAILS
    T = sindex % _NUM_TAILS
    return L, V, T


def _make_vowel_syllable_from(ch: str) -> str | None:
    d = _decompose_hangul(ch)
    if d is None:
        return None
    _, V, _ = d
    code = _HANGUL_BASE + ((_L_IEUNG_INDEX * _NUM_VOWELS + V) * _NUM_TAILS)
    return chr(code)


def _last_hangul_syllable_from_list(parts: list[str]) -> str | None:
    flat = "".join(parts)
    for ch in reversed(flat):
        if _is_hangul_syllable(ch):
            return ch
    return None


# compatibility jamo -> jongseong index
JONG = {
    "ㄱ": 1, "ㄲ": 2, "ㄳ": 3, "ㄴ": 4, "ㄵ": 5, "ㄶ": 6,
    "ㄷ": 7, "ㄹ": 8, "ㄺ": 9, "ㄻ": 10, "ㄼ": 11, "ㄽ": 12,
    "ㄾ": 13, "ㄿ": 14, "ㅀ": 15, "ㅁ": 16, "ㅂ": 17, "ㅄ": 18,
    "ㅅ": 19, "ㅆ": 20, "ㅇ": 21, "ㅈ": 22, "ㅊ": 23, "ㅋ": 24,
    "ㅌ": 25, "ㅍ": 26, "ㅎ": 27
}


def pack_final_jamo(text: str) -> str:
    """Pack trailing compatibility jamo (e.g., ㄴ) into the previous Hangul syllable as 받침 when possible.

    Example: "챠ㄴ" -> "챤"
    """
    out: list[str] = []
    for ch in text:
        if ch in JONG and out:
            prev = out[-1]
            if _is_hangul_syllable(prev):
                code = ord(prev)
                # jongseong index is the final-consonant slot (0 = none)
                jong = (code - _HANGUL_BASE) % _NUM_TAILS
                if jong == 0:
                    out[-1] = chr(code + JONG[ch])
                    continue
        out.append(ch)
    return "".join(out)

# Jongseong (final consonant) index -> compatibility jamo.
# Index 0 means "no final".
_JONG_TO_COMPAT = [
    "",   # 0
    "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ",
    "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
]

def unpack_final_jamo(text: str) -> str:
    """
    Convert Hangul syllables with 받침 into:
      (same syllable without 받침) + (compatibility jamo)

    Example: "챤" -> "챠ㄴ"
    """
    out: list[str] = []
    for ch in text:
        d = _decompose_hangul(ch)  # uses your existing utility
        if d is None:
            out.append(ch)
            continue

        L, V, T = d
        if T == 0:
            out.append(ch)
            continue

        # Rebuild the syllable with no final consonant (T=0)
        base_code = _HANGUL_BASE + ((L * _NUM_VOWELS + V) * _NUM_TAILS)  # same formula your decompose implies
        out.append(chr(base_code))

        # Append the detached final consonant as a separate jamo
        compat = _JONG_TO_COMPAT[T] if 0 <= T < len(_JONG_TO_COMPAT) else ""
        if compat:
            out.append(compat)

    return "".join(out)

# ============================================================
# Reverse maps (built from default profile)
# NOTE: If you change the default profile's outputs, these will
# follow that profile for reverse conversion.
# ============================================================

def _build_reverse_maps(from_map: dict[str, str]):
    h2hira: dict[str, str] = {}
    h2kata: dict[str, str] = {}
    for kana, han in from_map.items():
        first = kana[0]
        if "ぁ" <= first <= "ゟ":
            h2hira.setdefault(han, kana)
        if "ァ" <= first <= "ヿ":
            h2kata.setdefault(han, kana)
    return h2hira, h2kata

hangul_to_hiragana, hangul_to_katakana = _build_reverse_maps(KANA_TO_HANGUL_PROFILES["default"])
# Add mappings for compatibility final-jamo produced by unpack_final_jamo().
# This prevents leftovers like 'ㄱ' in outputs such as 한국 -> はんぐく / ハングク.
_FINAL_JAMO_TO_HIRA: dict[str, str] = {
    "ㄱ": "く", "ㄲ": "く", "ㅋ": "く", "ㄳ": "く", "ㄺ": "く",
    "ㄴ": "ん", "ㄵ": "ん", "ㄶ": "ん",
    "ㄷ": "と", "ㅌ": "と", "ㅅ": "す", "ㅆ": "す",
    "ㅈ": "つ", "ㅊ": "つ",
    "ㅎ": "ほ",
    "ㅁ": "む", "ㄻ": "む",
    "ㅂ": "ぷ", "ㅍ": "ぷ", "ㅄ": "ぷ", "ㄿ": "ぷ",
    "ㄹ": "る", "ㄼ": "る", "ㄽ": "る", "ㄾ": "る", "ㅀ": "る",
    "ㅇ": "ん",
}
_FINAL_JAMO_TO_KATA: dict[str, str] = {
    k: v.translate(str.maketrans({
        "く":"ク","ん":"ン","と":"ト","す":"ス","つ":"ツ","ほ":"ホ","む":"ム","ぷ":"プ","る":"ル"
    }))
    for k, v in _FINAL_JAMO_TO_HIRA.items()
}

hangul_to_hiragana.update(_FINAL_JAMO_TO_HIRA)
hangul_to_katakana.update(_FINAL_JAMO_TO_KATA)



# ============================================================
# Optional: sokuon helper (kana -> mix of kana + tense Hangul)
# ============================================================

def enable_sokuon_in_hangul(kana_text: str) -> str:
    """
    Replace っ/ッ + certain kana with tense Hangul syllables (까, 싸, 따, ...).
    """
    sokuon_map = {
        # Hiragana
        "か": "까", "き": "끼", "く": "꾸", "け": "께", "こ": "꼬",
        "さ": "싸", "し": "씨", "す": "쓰", "せ": "쎄", "そ": "쏘",
        "た": "따", "ち": "찌", "つ": "쯔", "て": "떼", "と": "또",
        "ぱ": "빠", "ぴ": "삐", "ぷ": "뿌", "ぺ": "뻬", "ぽ": "뽀",
        # Katakana
        "カ": "까", "キ": "끼", "ク": "꾸", "ケ": "께", "コ": "꼬",
        "サ": "싸", "シ": "씨", "ス": "쓰", "セ": "쎄", "ソ": "쏘",
        "タ": "따", "チ": "찌", "ツ": "쯔", "テ": "떼", "ト": "또",
        "パ": "빠", "ピ": "삐", "プ": "뿌", "ペ": "뻬", "ポ": "뽀",
    }

    out: list[str] = []
    i = 0
    n = len(kana_text)
    while i < n:
        ch = kana_text[i]
        if ch in ("っ", "ッ") and i + 1 < n:
            nxt = kana_text[i + 1]
            if nxt in sokuon_map:
                out.append(sokuon_map[nxt])
                i += 2
                continue
        out.append(ch)
        i += 1
    return "".join(out)

# ============================================================
# Kana -> Hangul (core + modes + profiles)
# ============================================================

def _kana_to_hangul_core(text: str, *, double_vowel: bool, hangul_profile: str) -> str:
    """Core Kana->Hangul converter.

    Optimizations vs. the original:
    - Track the last Hangul syllable incrementally (avoids O(n^2) joins when processing many 'ー').
    """
    mapping = KANA_TO_HANGUL_PROFILES.get(hangul_profile, KANA_TO_HANGUL_PROFILES["default"])

    result: list[str] = []
    i = 0
    n = len(text)

    last_hangul: str | None = None

    def _update_last_hangul(appended: str) -> None:
        nonlocal last_hangul
        for c in reversed(appended):
            if _is_hangul_syllable(c):
                last_hangul = c
                return

    while i < n:
        ch = text[i]

        # Long vowel mark
        if ch == "ー":
            if double_vowel and last_hangul is not None:
                v = _make_vowel_syllable_from(last_hangul)
                if v:
                    result.append(v)
                    last_hangul = v
            i += 1
            continue

        # Ignore sokuon here (handled in tense modes)
        if ch in ("っ", "ッ"):
            i += 1
            continue

        # Try 2-char combo
        if i + 1 < n:
            pair = text[i:i + 2]
            mapped = mapping.get(pair)
            if mapped is not None:
                result.append(mapped)
                _update_last_hangul(mapped)
                i += 2
                continue

        # Fallback single
        mapped = mapping.get(ch, ch)
        result.append(mapped)
        _update_last_hangul(mapped)
        i += 1

    return "".join(result)

def kana_to_hangul_text(
    text: str,
    mode: str = "simple",
    hangul_profile: str = "default",
) -> str:
    """
    Convert Kana -> Hangul.

    mode:
      - "simple": no tense consonants, no explicit long vowels
      - "tense": sokuon -> tense Hangul syllable (approx)
      - "double_vowel": ー -> extra vowel syllable
      - "tense_double": both
    hangul_profile:
      - "default" or any key in hangul_profile_overrides
    """
    mode = mode.lower()
    src = enable_sokuon_in_hangul(text) if mode in ("tense", "tense_double") else text

    core = _kana_to_hangul_core(
        src,
        double_vowel=("double" in mode),
        hangul_profile=hangul_profile,
    )
    return pack_final_jamo(core)

# ============================================================
# Hangul -> Kana (Katakana can optionally collapse long vowels)
# ============================================================

def hangul_to_hiragana_text(text: str) -> str:
    text = unpack_final_jamo(text)
    return "".join(hangul_to_hiragana.get(ch, ch) for ch in text)


def hangul_to_katakana_text(text: str, long_vowels: str | None = None) -> str:
    """
    If long_vowels == "ー", collapse:
      S1 + S2 where S2 is vowel-only with the same vowel as S1
    into: kana(S1) + "ー"
    """
    text = unpack_final_jamo(text)
    out: list[str] = []
    i = 0
    n = len(text)

    while i < n:
        ch = text[i]

        if (
            long_vowels == "ー"
            and i + 1 < n
            and _is_hangul_syllable(ch)
            and _is_hangul_syllable(text[i + 1])
        ):
            d1 = _decompose_hangul(ch)
            d2 = _decompose_hangul(text[i + 1])
            if d1 and d2:
                L1, V1, T1 = d1
                L2, V2, T2 = d2
                if L2 == _L_IEUNG_INDEX and T2 == 0 and V1 == V2:
                    out.append(hangul_to_katakana.get(ch, ch))
                    out.append("ー")
                    i += 2
                    continue

        out.append(hangul_to_katakana.get(ch, ch))
        i += 1

    return "".join(out)

# ============================================================
# Kana <-> Romaji mappings + styles
# ============================================================

kana_to_romaji_hepburn: dict[str, str] = {
    # Vowels
    "あ": "a", "ア": "a", "ぁ": "a", "ァ": "a",
    "い": "i", "イ": "i", "ぃ": "i", "ィ": "i",
    "う": "u", "ウ": "u", "ぅ": "u", "ゥ": "u",
    "え": "e", "エ": "e", "ぇ": "e", "ェ": "e",
    "お": "o", "オ": "o", "ぉ": "o", "ォ": "o",

    # K
    "か": "ka", "カ": "ka", "き": "ki", "キ": "ki", "く": "ku", "ク": "ku", "け": "ke", "ケ": "ke", "こ": "ko", "コ": "ko",
    "きゃ": "kya", "キャ": "kya", "きゅ": "kyu", "キュ": "kyu", "きょ": "kyo", "キョ": "kyo",

    # S
    "さ": "sa", "サ": "sa", "し": "shi", "シ": "shi", "す": "su", "ス": "su", "せ": "se", "セ": "se", "そ": "so", "ソ": "so",
    "しゃ": "sha", "シャ": "sha", "しゅ": "shu", "シュ": "shu", "しょ": "sho", "ショ": "sho",

    # T
    "た": "ta", "タ": "ta", "ち": "chi", "チ": "chi", "つ": "tsu", "ツ": "tsu", "て": "te", "テ": "te", "と": "to", "ト": "to",
    "ちゃ": "cha", "チャ": "cha", "ちゅ": "chu", "チュ": "chu", "ちょ": "cho", "チョ": "cho",

    # N
    "な": "na", "ナ": "na", "に": "ni", "ニ": "ni", "ぬ": "nu", "ヌ": "nu", "ね": "ne", "ネ": "ne", "の": "no", "ノ": "no",
    "ん": "n", "ン": "n",
    "にゃ": "nya", "ニャ": "nya", "にゅ": "nyu", "ニュ": "nyu", "にょ": "nyo", "ニョ": "nyo",

    # H
    "は": "ha", "ハ": "ha", "ひ": "hi", "ヒ": "hi", "ふ": "fu", "フ": "fu", "へ": "he", "ヘ": "he", "ほ": "ho", "ホ": "ho",
    "ひゃ": "hya", "ヒャ": "hya", "ひゅ": "hyu", "ヒュ": "hyu", "ひょ": "hyo", "ヒョ": "hyo",

    # M
    "ま": "ma", "マ": "ma", "み": "mi", "ミ": "mi", "む": "mu", "ム": "mu", "め": "me", "メ": "me", "も": "mo", "モ": "mo",
    "みゃ": "mya", "ミャ": "mya", "みゅ": "myu", "ミュ": "myu", "みょ": "myo", "ミョ": "myo",

    # Y
    "や": "ya", "ヤ": "ya", "ゃ": "ya", "ャ": "ya",
    "ゆ": "yu", "ユ": "yu", "ゅ": "yu", "ュ": "yu",
    "よ": "yo", "ヨ": "yo", "ょ": "yo", "ョ": "yo",

    # R
    "ら": "ra", "ラ": "ra", "り": "ri", "リ": "ri", "る": "ru", "ル": "ru", "れ": "re", "レ": "re", "ろ": "ro", "ロ": "ro",
    "りゃ": "rya", "リャ": "rya", "りゅ": "ryu", "リュ": "ryu", "りょ": "ryo", "リョ": "ryo",

    # W & historical
    "わ": "wa", "ワ": "wa", "を": "wo", "ヲ": "wo", "ゑ": "we", "ヱ": "we", "ゐ": "wi", "ヰ": "wi",
    
    # Vu (added)
    "ゔ": "vu", "ヴ": "vu",

    # G
    "が": "ga", "ガ": "ga", "ぎ": "gi", "ギ": "gi", "ぐ": "gu", "グ": "gu", "げ": "ge", "ゲ": "ge", "ご": "go", "ゴ": "go",
    "ぎゃ": "gya", "ギャ": "gya", "ぎゅ": "gyu", "ギュ": "gyu", "ぎょ": "gyo", "ギョ": "gyo",

    # Z/J
    "ざ": "za", "ザ": "za", "じ": "ji", "ジ": "ji", "ず": "zu", "ズ": "zu", "ぜ": "ze", "ゼ": "ze", "ぞ": "zo", "ゾ": "zo",
    "じゃ": "ja", "ジャ": "ja", "じゅ": "ju", "ジュ": "ju", "じょ": "jo", "ジョ": "jo",

    # D
    "だ": "da", "ダ": "da", "ぢ": "ji", "ヂ": "ji", "づ": "zu", "ヅ": "zu", "で": "de", "デ": "de", "ど": "do", "ド": "do",

    # B
    "ば": "ba", "バ": "ba", "び": "bi", "ビ": "bi", "ぶ": "bu", "ブ": "bu", "べ": "be", "ベ": "be", "ぼ": "bo", "ボ": "bo",
    "びゃ": "bya", "ビャ": "bya", "びゅ": "byu", "ビュ": "byu", "びょ": "byo", "ビョ": "byo",

    # P
    "ぱ": "pa", "パ": "pa", "ぴ": "pi", "ピ": "pi", "ぷ": "pu", "プ": "pu", "ぺ": "pe", "ペ": "pe", "ぽ": "po", "ポ": "po",
    "ぴゃ": "pya", "ピャ": "pya", "ぴゅ": "pyu", "ピュ": "pyu", "ぴょ": "pyo", "ピョ": "pyo",
}

kana_to_romaji_kunrei: dict[str, str] = copy.deepcopy(kana_to_romaji_hepburn)
kana_to_romaji_kunrei.update({
    "し": "si", "シ": "si",
    "しゃ": "sya", "シャ": "sya",
    "しゅ": "syu", "シュ": "syu",
    "しょ": "syo", "ショ": "syo",
    "ち": "ti", "チ": "ti",
    "ちゃ": "tya", "チャ": "tya",
    "ちゅ": "tyu", "チュ": "tyu",
    "ちょ": "tyo", "チョ": "tyo",
    "つ": "tu", "ツ": "tu",
    "ふ": "hu", "フ": "hu",
    "じ": "zi", "ジ": "zi",
    "ぢ": "zi", "ヂ": "zi",
    "じゃ": "zya", "ジャ": "zya",
    "じゅ": "zyu", "ジュ": "zyu",
    "じょ": "zyo", "ジョ": "zyo",
})


kana_to_romaji_nihon: dict[str, str] = copy.deepcopy(kana_to_romaji_hepburn)
kana_to_romaji_nihon.update({
    # Nihon-shiki largely matches Kunrei-shiki, but keeps ぢ/づ distinct.
    "し": "si", "シ": "si",
    "しゃ": "sya", "シャ": "sya",
    "しゅ": "syu", "シュ": "syu",
    "しょ": "syo", "ショ": "syo",
    "ち": "ti", "チ": "ti",
    "ちゃ": "tya", "チャ": "tya",
    "ちゅ": "tyu", "チュ": "tyu",
    "ちょ": "tyo", "チョ": "tyo",
    "つ": "tu", "ツ": "tu",
    "ふ": "hu", "フ": "hu",
    "じ": "zi", "ジ": "zi",
    "ぢ": "di", "ヂ": "di",
    "じゃ": "zya", "ジャ": "zya",
    "じゅ": "zyu", "ジュ": "zyu",
    "じょ": "zyo", "ジョ": "zyo",
    "ぢゃ": "dya", "ヂャ": "dya",
    "ぢゅ": "dyu", "ヂュ": "dyu",
    "ぢょ": "dyo", "ヂョ": "dyo",
    "づ": "du", "ヅ": "du",
    "づぁ": "dua", "ヅァ": "dua",
    "づぃ": "dui", "ヅィ": "dui",
    "づぇ": "due", "ヅェ": "due",
    "づぉ": "duo", "ヅォ": "duo",
})


ROMAJI_STYLES: dict[str, dict[str, str]] = {
    "hepburn": kana_to_romaji_hepburn,
    "kunrei": kana_to_romaji_kunrei,
    "nihon": kana_to_romaji_nihon,
}

ROMAJI_STYLE_ALIASES: dict[str, str] = {
    # Hepburn
    "hepburn": "hepburn",
    "modified-hepburn": "hepburn",
    "traditional-hepburn": "hepburn",
    "hb": "hepburn",
    # Kunrei-shiki
    "kunrei": "kunrei",
    "kunrei-shiki": "kunrei",
    "kunreishiki": "kunrei",
    "ks": "kunrei",
    # Nihon-shiki
    "nihon": "nihon",
    "nihon-shiki": "nihon",
    "nihonshiki": "nihon",
    "ns": "nihon",
}

def _normalize_romaji_style(style: str | None) -> str:
    """Normalize romaji style name (supports aliases)."""
    key = (style or "hepburn").strip().lower().replace("_", "-")
    return ROMAJI_STYLE_ALIASES.get(key, key)



romaji_to_hiragana_by_style: dict[str, dict[str, str]] = {}
romaji_to_katakana_by_style: dict[str, dict[str, str]] = {}

def _build_romaji_reverse_tables() -> None:
    # Build per-style reverse maps (romaji -> kana) using "first occurrence wins"
    # to reduce ambiguity. Greedy matching later prefers longer keys.
    for style_name, k2r in ROMAJI_STYLES.items():
        hira: dict[str, str] = {}
        kata: dict[str, str] = {}
        for kana, ro in k2r.items():
            first = kana[0]
            key = ro.lower()
            if "ぁ" <= first <= "ゟ":
                hira.setdefault(key, kana)
            if "ァ" <= first <= "ヿ":
                kata.setdefault(key, kana)
        romaji_to_hiragana_by_style[style_name] = hira
        romaji_to_katakana_by_style[style_name] = kata

_build_romaji_reverse_tables()

# Back-compat (default Hepburn)
romaji_to_hiragana: dict[str, str] = romaji_to_hiragana_by_style["hepburn"]
romaji_to_katakana: dict[str, str] = romaji_to_katakana_by_style["hepburn"]

# ============================================================
# Kana -> Romaji (with sokuon + long vowels) + style choice
# ============================================================

def kana_to_romaji_text(text: str, style: str = "hepburn") -> str:
    style = _normalize_romaji_style(style)
    """Kana -> romaji.

    Features:
    - っ/ッ -> doubled consonant
    - ー   -> repeat last vowel
    - style: "hepburn" | "kunrei" | any key in ROMAJI_STYLES

    Optimization vs. the original:
    - Tracks the last vowel incrementally (avoids O(n^2) joins when processing many 'ー').
    """
    style = style.lower()
    mapping = ROMAJI_STYLES.get(style, kana_to_romaji_hepburn)

    result: list[str] = []
    i = 0
    n = len(text)
    vowels = "aeiou"
    last_vowel: str | None = None

    def _push(ro: str) -> None:
        nonlocal last_vowel
        result.append(ro)
        for c in reversed(ro):
            if c in vowels:
                last_vowel = c
                break

    while i < n:
        ch = text[i]

        if ch == "ー":
            if last_vowel:
                result.append(last_vowel)
            i += 1
            continue

        if ch in ("っ", "ッ"):
            if i + 1 < n:
                next_ro: str | None = None
                if i + 2 < n:
                    pair = text[i + 1:i + 3]
                    next_ro = mapping.get(pair)
                if next_ro is None:
                    next_ro = mapping.get(text[i + 1])

                if next_ro:
                    for c in next_ro:
                        if c not in vowels:
                            result.append(c)
                            break
            i += 1
            continue

        if i + 1 < n:
            pair = text[i:i + 2]
            mapped = mapping.get(pair)
            if mapped is not None:
                _push(mapped)
                i += 2
                continue

        _push(mapping.get(ch, ch))
        i += 1

    return "".join(result)

# ============================================================
# Romaji -> Kana (Hepburn input)
# ============================================================

def _romaji_to_kana_generic(text: str, table: dict[str, str], sokuon_char: str) -> str:
    """Romaji -> kana using greedy matching.

    Rules:
    - Double consonants => sokuon (っ / ッ), except 'nn' (which can represent ん).
    - Supports "n'" (n + apostrophe) => ん.
    """
    s = text.lower()
    out: list[str] = []
    i = 0
    n = len(s)
    vowels = "aeiou"
    maxlen = max((len(k) for k in table.keys()), default=1)

    while i < n:
        # n' => ん
        if s[i] == "n" and i + 1 < n and s[i + 1] == "'":
            out.append("ん" if sokuon_char == "っ" else "ン")
            i += 2
            continue

        # nn handling:
        # - If 'nn' is followed by a vowel or 'y', interpret as ん + (next syllable starting with n...)
        #   so we only consume the first 'n' (leaving the second for matching 'na/ni/nya', etc.).
        # - Otherwise, consume both.
        if s[i] == "n" and i + 1 < n and s[i + 1] == "n":
            out.append("ん" if sokuon_char == "っ" else "ン")
            if i + 2 < n and (s[i + 2] in vowels or s[i + 2] == "y"):
                i += 1
            else:
                i += 2
            continue

        # Single n before a consonant (or end) => ん
        if s[i] == "n" and (i + 1 == n or (s[i + 1] not in vowels and s[i + 1] != "y")):
            out.append("ん" if sokuon_char == "っ" else "ン")
            i += 1
            continue

        # Double consonant (except n) => sokuon
        if (
            i + 1 < n
            and s[i] == s[i + 1]
            and s[i].isalpha()
            and s[i] not in vowels
            and s[i] != "n"
        ):
            out.append(sokuon_char)
            i += 1
            continue

        matched = False
        # Greedy match up to max key length
        for size in range(min(maxlen, n - i), 0, -1):
            chunk = s[i:i + size]
            kana = table.get(chunk)
            if kana is not None:
                out.append(kana)
                i += size
                matched = True
                break

        if not matched:
            out.append(text[i])  # preserve original character/case for unknowns
            i += 1

    return "".join(out)


def romaji_to_hiragana_text(text: str, style: str = "hepburn") -> str:
    style = _normalize_romaji_style(style)
    table = romaji_to_hiragana_by_style.get(style.lower(), romaji_to_hiragana)
    return _romaji_to_kana_generic(text, table, "っ")


def romaji_to_katakana_text(text: str, style: str = "hepburn") -> str:
    style = _normalize_romaji_style(style)
    table = romaji_to_katakana_by_style.get(style.lower(), romaji_to_katakana)
    return _romaji_to_kana_generic(text, table, "ッ")

# ============================================================
# Hangul -> Romaji via Hiragana (style choice)
# ============================================================

def hangul_to_romaji_text(text: str, style: str = "hepburn") -> str:
    hira = hangul_to_hiragana_text(text)
    return kana_to_romaji_text(hira, style=style)


def romaji_to_hangul_text(text: str, mode: str = "simple", hangul_profile: str = "default", *, style: str = "hepburn") -> str:
    style = _normalize_romaji_style(style)
    hira = romaji_to_hiragana_text(text, style=style)
    return kana_to_hangul_text(hira, mode=mode, hangul_profile=hangul_profile)

# ============================================================
# Public API
# ============================================================

__all__ = [
    # kana <-> hangul
    "kana_to_hangul_text",
    "hangul_to_hiragana_text",
    "hangul_to_katakana_text",
    "enable_sokuon_in_hangul",

    # kana <-> romaji
    "kana_to_romaji_text",
    "romaji_to_hiragana_text",
    "romaji_to_katakana_text",

    # hangul <-> romaji
    "hangul_to_romaji_text",
    "romaji_to_hangul_text",

    # profiles/styles
    "hangul_profile_overrides",
    "ROMAJI_STYLES",
]

# ============================================================
# Demo
# ============================================================



# -----------------------------
# File-aware convenience wrappers
# -----------------------------


def hangul_to_hiragana_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `hangul_to_hiragana_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `hangul_to_hiragana_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = hangul_to_hiragana_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def hangul_to_katakana_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `hangul_to_katakana_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `hangul_to_katakana_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = hangul_to_katakana_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def hangul_to_romaji_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `hangul_to_romaji_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `hangul_to_romaji_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = hangul_to_romaji_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def hangul_to_kroman_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `hangul_to_kroman_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `hangul_to_kroman_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = hangul_to_kroman_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def kroman_to_hangul_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `kroman_to_hangul_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `kroman_to_hangul_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = kroman_to_hangul_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def kana_to_romaji_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `kana_to_romaji_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `kana_to_romaji_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = kana_to_romaji_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def romaji_to_hiragana_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `romaji_to_hiragana_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `romaji_to_hiragana_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = romaji_to_hiragana_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def romaji_to_katakana_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `romaji_to_katakana_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `romaji_to_katakana_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = romaji_to_katakana_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def romaji_to_hangul_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `romaji_to_hangul_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `romaji_to_hangul_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = romaji_to_hangul_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)


def kana_to_hangul_source(*, text: str | None = None, file: str | Path | None = None, out_file: str | Path | None = None, encoding: str = "utf-8", **kwargs) -> str:
    """Like `kana_to_hangul_text` but reads input from `text` or `file`.

    Args:
        text: Input string.
        file: Path to input text file.
        out_file: Optional path to write the result.
        encoding: File encoding for read/write.
        **kwargs: Forwarded to `kana_to_hangul_text` (e.g., system/style/variant/syllable_sep/etc.).
    """
    src = _read_text_source(text=text, file=file, encoding=encoding)
    res = kana_to_hangul_text(src, **kwargs)
    return _write_text_dest(res, out_file, encoding=encoding)

if __name__ == "__main__":
    import argparse
    import sys

    MODES = [
        "hangul_to_hiragana",
        "hangul_to_katakana",
        "hangul_to_kana",
        "hangul_to_romaji",
        "hangul_to_kroman",
        "kroman_to_hangul",
        "kana_to_hangul",
        "kana_to_romaji",
        "romaji_to_hiragana",
        "romaji_to_katakana",
        "romaji_to_hangul",
    ]

    parser = argparse.ArgumentParser(
        prog="kanahangul",
        description="Kana/Hangul/Romanization conversion CLI (supports file or stdin).",
    )
    parser.add_argument(
        "mode",
        choices=MODES,
        help="Conversion mode.",
    )
    parser.add_argument(
        "-t", "--text",
        help="Input text (mutually exclusive with --in). If omitted and --in is not set, reads from stdin.",
    )
    parser.add_argument(
        "-i", "--in",
        dest="in_file",
        help="Input file path (mutually exclusive with --text).",
    )
    parser.add_argument(
        "-o", "--out",
        dest="out_file",
        help="Output file path (if omitted, prints to stdout).",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="File encoding for --in/--out (default: utf-8).",
    )

    # Common kwargs (only used by some modes)
    parser.add_argument("--system", default="rr", help="Romanization system (e.g., rr, mr, ala-lc, nk1992, yale).")
    parser.add_argument("--variant", default="reversible", help="Variant (reversible or official).")
    parser.add_argument("--syllable-sep", default="-", help="Syllable separator for reversible output (default: '-').")
    parser.add_argument("--split-words", action="store_true", help="Apply word-division logic (official mode).")
    parser.add_argument("--word-sep-policy", default="keep",
                        help="Separator output policy: keep|space|hyphenate|smart|smart_hyphenate.")
    parser.add_argument("--boundary-mode", default="whitespace_punct",
                        help="Word boundary mode for official: whitespace|whitespace_punct|custom.")
    parser.add_argument("--boundary-chars", default=None,
                        help="Custom boundary chars when --boundary-mode=custom.")
    parser.add_argument("--style", default="hepburn", help="Romaji style: hepburn|kunrei|nihon (aliases supported).")

    args = parser.parse_args()

    # Resolve input
    if args.text is not None and args.in_file is not None:
        parser.error("Use only one of --text or --in.")
    if args.text is None and args.in_file is None:
        input_text = sys.stdin.read()
    else:
        input_text = _read_text_source(text=args.text, file=args.in_file, encoding=args.encoding)

    mode = args.mode

    # Dispatch table
    if mode == "hangul_to_hiragana":
        result = hangul_to_hiragana_text(input_text)
    elif mode == "hangul_to_katakana":
        result = hangul_to_katakana_text(input_text)
    elif mode == "hangul_to_kana":
        result = hangul_to_kana_text(input_text)
    elif mode == "hangul_to_romaji":
        result = hangul_to_romaji_text(input_text, style=args.style)
    elif mode == "hangul_to_kroman":
        result = hangul_to_kroman_text(
            input_text,
            system=args.system,
            variant=args.variant,
            syllable_sep=args.syllable_sep,
            split_words=args.split_words,
            word_sep_policy=args.word_sep_policy,
            boundary_mode=args.boundary_mode,
            boundary_chars=args.boundary_chars,
        )
    elif mode == "kroman_to_hangul":
        result = kroman_to_hangul_text(input_text, system=args.system)
    elif mode == "kana_to_hangul":
        result = kana_to_hangul_text(input_text)
    elif mode == "kana_to_romaji":
        result = kana_to_romaji_text(input_text, style=args.style)
    elif mode == "romaji_to_hiragana":
        result = romaji_to_hiragana_text(input_text, style=args.style)
    elif mode == "romaji_to_katakana":
        result = romaji_to_katakana_text(input_text, style=args.style)
    elif mode == "romaji_to_hangul":
        result = romaji_to_hangul_text(input_text, style=args.style)
    else:
        parser.error(f"Unsupported mode: {mode}")

    # Output
    if args.out_file:
        _write_text_dest(result, args.out_file, encoding=args.encoding)
    else:
        sys.stdout.write(result)
