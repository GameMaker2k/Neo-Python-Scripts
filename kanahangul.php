<?php
declare(strict_types=1);

/**
 * kanahangul.php (single-file demo)
 * - Kana -> Hangul: simple / tense / double_vowel / tense_double
 * - Hangul -> Hiragana
 * - Hangul -> Katakana (+ optional long-vowel collapse "ー")
 *
 * Make sure this file is saved as UTF-8.
 */

mb_internal_encoding('UTF-8');
mb_regex_encoding('UTF-8');

/* -----------------------------
 * UTF-8 helpers (no intl needed)
 * ----------------------------- */
function u_chars(string $s): array {
  if ($s === '') return [];
  return preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY) ?: [];
}
function u_ord(string $ch): int {
  $u = mb_convert_encoding($ch, 'UCS-4BE', 'UTF-8');
  $arr = unpack('N', $u);
  return (int)($arr[1] ?? 0);
}
function u_chr(int $code): string {
  return mb_convert_encoding(pack('N', $code), 'UTF-8', 'UCS-4BE');
}

/* -----------------------------
 * Hangul syllable utilities
 * ----------------------------- */
const HANGUL_BASE = 0xAC00;
const HANGUL_LAST = 0xD7A3;
const NUM_ONSETS  = 19;
const NUM_VOWELS  = 21;
const NUM_TAILS   = 28;
const L_IEUNG_INDEX = 11; // ㅇ initial

function is_hangul_syllable(string $ch): bool {
  $o = u_ord($ch);
  return (HANGUL_BASE <= $o && $o <= HANGUL_LAST);
}
function decompose_hangul(string $ch): ?array {
  $o = u_ord($ch);
  if (! (HANGUL_BASE <= $o && $o <= HANGUL_LAST)) return null;
  $sindex = $o - HANGUL_BASE;
  $L = intdiv($sindex, (NUM_VOWELS * NUM_TAILS));
  $V = intdiv(($sindex % (NUM_VOWELS * NUM_TAILS)), NUM_TAILS);
  $T = $sindex % NUM_TAILS;
  return [$L, $V, $T];
}
function make_vowel_syllable_from(string $ch): ?string {
  $d = decompose_hangul($ch);
  if ($d === null) return null;
  [, $V, ] = $d;
  $code = HANGUL_BASE + ((L_IEUNG_INDEX * NUM_VOWELS + $V) * NUM_TAILS);
  return u_chr($code);
}

/* -----------------------------
 * Final-jamo pack/unpack
 * ----------------------------- */
$JONG = [
  "ㄱ"=>1,"ㄲ"=>2,"ㄳ"=>3,"ㄴ"=>4,"ㄵ"=>5,"ㄶ"=>6,
  "ㄷ"=>7,"ㄹ"=>8,"ㄺ"=>9,"ㄻ"=>10,"ㄼ"=>11,"ㄽ"=>12,
  "ㄾ"=>13,"ㄿ"=>14,"ㅀ"=>15,"ㅁ"=>16,"ㅂ"=>17,"ㅄ"=>18,
  "ㅅ"=>19,"ㅆ"=>20,"ㅇ"=>21,"ㅈ"=>22,"ㅊ"=>23,"ㅋ"=>24,
  "ㅌ"=>25,"ㅍ"=>26,"ㅎ"=>27
];

$JONG_TO_COMPAT = [
  "", "ㄱ","ㄲ","ㄳ","ㄴ","ㄵ","ㄶ","ㄷ","ㄹ","ㄺ","ㄻ","ㄼ","ㄽ","ㄾ","ㄿ","ㅀ",
  "ㅁ","ㅂ","ㅄ","ㅅ","ㅆ","ㅇ","ㅈ","ㅊ","ㅋ","ㅌ","ㅍ","ㅎ"
];

function pack_final_jamo(string $text, array $JONG): string {
  $out = [];
  foreach (u_chars($text) as $ch) {
    if (isset($JONG[$ch]) && !empty($out)) {
      $prev = $out[count($out)-1];
      if (is_hangul_syllable($prev)) {
        $code = u_ord($prev);
        $jong = ($code - HANGUL_BASE) % NUM_TAILS;
        if ($jong === 0) {
          $out[count($out)-1] = u_chr($code + $JONG[$ch]);
          continue;
        }
      }
    }
    $out[] = $ch;
  }
  return implode("", $out);
}

function unpack_final_jamo(string $text, array $JONG_TO_COMPAT): string {
  $out = [];
  foreach (u_chars($text) as $ch) {
    $d = decompose_hangul($ch);
    if ($d === null) { $out[] = $ch; continue; }
    [$L,$V,$T] = $d;
    if ($T === 0) { $out[] = $ch; continue; }

    $base_code = HANGUL_BASE + (($L * NUM_VOWELS + $V) * NUM_TAILS);
    $out[] = u_chr($base_code);

    $compat = ($T >= 0 && $T < count($JONG_TO_COMPAT)) ? $JONG_TO_COMPAT[$T] : "";
    if ($compat !== "") $out[] = $compat;
  }
  return implode("", $out);
}

/* -----------------------------
 * Kana -> Hangul mapping (base + profiles)
 * ----------------------------- */
$kana_to_hangul_base = [
  // --- Basic vowels (incl. small vowels) ---
  "あ"=>"아","ア"=>"아","ぁ"=>"아","ァ"=>"아",
  "い"=>"이","イ"=>"이","ぃ"=>"이","ィ"=>"이",
  "う"=>"우","ウ"=>"우","ぅ"=>"우","ゥ"=>"우",
  "え"=>"에","エ"=>"에","ぇ"=>"에","ェ"=>"에",
  "お"=>"오","オ"=>"오","ぉ"=>"오","ォ"=>"오",

  // --- K row ---
  "か"=>"카","カ"=>"카","き"=>"키","キ"=>"키","く"=>"쿠","ク"=>"쿠","け"=>"케","ケ"=>"케","こ"=>"코","コ"=>"코",
  "きゃ"=>"캬","キャ"=>"캬","きゅ"=>"큐","キュ"=>"큐","きょ"=>"쿄","キョ"=>"쿄",

  // --- S row ---
  "さ"=>"사","サ"=>"사","し"=>"시","シ"=>"시","す"=>"스","ス"=>"스","せ"=>"세","セ"=>"세","そ"=>"소","ソ"=>"소",
  "しゃ"=>"샤","シャ"=>"샤","しゅ"=>"슈","シュ"=>"슈","しょ"=>"쇼","ショ"=>"쇼",

  // --- T row ---
  "た"=>"타","タ"=>"타","ち"=>"치","チ"=>"치","つ"=>"츠","ツ"=>"츠","て"=>"테","テ"=>"테","と"=>"토","ト"=>"토",
  "ちゃ"=>"챠","チャ"=>"챠","ちゅ"=>"츄","チュ"=>"츄","ちょ"=>"쵸","チョ"=>"쵸",

  // --- N row ---
  "な"=>"나","ナ"=>"나","に"=>"니","ニ"=>"니","ぬ"=>"누","ヌ"=>"누","ね"=>"네","ネ"=>"네","の"=>"노","ノ"=>"노",
  "ん"=>"ㄴ","ン"=>"ㄴ",
  "にゃ"=>"냐","ニャ"=>"냐","にゅ"=>"뉴","ニュ"=>"뉴","にょ"=>"뇨","ニョ"=>"뇨",

  // --- H row ---
  "は"=>"하","ハ"=>"하","ひ"=>"히","ヒ"=>"히","ふ"=>"후","フ"=>"후","へ"=>"헤","ヘ"=>"헤","ほ"=>"호","ホ"=>"호",
  "ひゃ"=>"햐","ヒャ"=>"햐","ひゅ"=>"휴","ヒュ"=>"휴","ひょ"=>"효","ヒョ"=>"효",

  // --- M row ---
  "ま"=>"마","マ"=>"마","み"=>"미","ミ"=>"미","む"=>"무","ム"=>"무","め"=>"메","メ"=>"메","も"=>"모","モ"=>"모",
  "みゃ"=>"먀","ミャ"=>"먀","みゅ"=>"뮤","ミュ"=>"뮤","みょ"=>"묘","ミョ"=>"묘",

  // --- Y row ---
  "や"=>"야","ヤ"=>"야","ゃ"=>"야","ャ"=>"야",
  "ゆ"=>"유","ユ"=>"유","ゅ"=>"유","ュ"=>"유",
  "よ"=>"요","ヨ"=>"요","ょ"=>"요","ョ"=>"요",

  // --- R row ---
  "ら"=>"라","ラ"=>"라","り"=>"리","リ"=>"리","る"=>"루","ル"=>"루","れ"=>"레","レ"=>"레","ろ"=>"로","ロ"=>"로",
  "りゃ"=>"랴","リャ"=>"랴","りゅ"=>"류","リュ"=>"류","りょ"=>"료","リョ"=>"료",

  // --- W row & historical ---
  "わ"=>"와","ワ"=>"와",
  "を"=>"오","ヲ"=>"오",
  "ゑ"=>"웨","ヱ"=>"웨",
  "ゐ"=>"위","ヰ"=>"위",

  // Vu (added)
  "ゔ"=>"부","ヴ"=>"부",

  // --- G row ---
  "が"=>"가","ガ"=>"가","ぎ"=>"기","ギ"=>"기","ぐ"=>"구","グ"=>"구","げ"=>"게","ゲ"=>"게","ご"=>"고","ゴ"=>"고",
  "ぎゃ"=>"갸","ギャ"=>"갸","ぎゅ"=>"규","ギュ"=>"규","ぎょ"=>"교","ギョ"=>"교",

  // --- Z/J row ---
  "ざ"=>"자","ザ"=>"자","じ"=>"지","ジ"=>"지","ず"=>"즈","ズ"=>"즈","ぜ"=>"제","ゼ"=>"제","ぞ"=>"조","ゾ"=>"조",
  "じゃ"=>"쟈","ジャ"=>"쟈","じゅ"=>"쥬","ジュ"=>"쥬","じょ"=>"죠","ジョ"=>"죠",

  // --- D row ---
  "だ"=>"다","ダ"=>"다","ぢ"=>"지","ヂ"=>"지","づ"=>"즈","ヅ"=>"즈","で"=>"데","デ"=>"데","ど"=>"도","ド"=>"도",

  // --- B row ---
  "ば"=>"바","バ"=>"바","び"=>"비","ビ"=>"비","ぶ"=>"부","ブ"=>"부","べ"=>"베","ベ"=>"베","ぼ"=>"보","ボ"=>"보",
  "びゃ"=>"뱌","ビャ"=>"뱌","びゅ"=>"뷰","ビュ"=>"뷰","びょ"=>"뵤","ビョ"=>"뵤",

  // --- P row ---
  "ぱ"=>"파","パ"=>"파","ぴ"=>"피","ピ"=>"피","ぷ"=>"푸","プ"=>"푸","ぺ"=>"페","ペ"=>"페","ぽ"=>"포","ポ"=>"포",
  "ぴゃ"=>"퍄","ピャ"=>"퍄","ぴゅ"=>"퓨","ピュ"=>"퓨","ぴょ"=>"표","ピョ"=>"표",
];

$hangul_profile_overrides = [
  "default" => [],
  "strict" => [],
  "loanword_kr" => [],
  "shi_ssi" => [
    "し"=>"씨","シ"=>"씨",
    "しゃ"=>"쌰","シャ"=>"쌰",
    "しゅ"=>"쓔","シュ"=>"쓔",
    "しょ"=>"쑈","ショ"=>"쑈",
  ],
  "tsu_sseu" => [
    "つ"=>"쓰","ツ"=>"쓰",
  ],
  "shi_ssi_tsu_sseu" => [
    "し"=>"씨","シ"=>"씨",
    "しゃ"=>"쌰","シャ"=>"쌰",
    "しゅ"=>"쓔","シュ"=>"쓔",
    "しょ"=>"쑈","ショ"=>"쑈",
    "つ"=>"쓰","ツ"=>"쓰",
  ],
  "ja_simple" => [
    "じゃ"=>"자","ジャ"=>"자",
    "じゅ"=>"주","ジュ"=>"주",
    "じょ"=>"조","ジョ"=>"조",
  ],
  "cha_chya" => [
    "ちゃ"=>"차","チャ"=>"차",
    "ちゅ"=>"추","チュ"=>"추",
    "ちょ"=>"초","チョ"=>"초",
  ],
  "korean_media" => [
    "し"=>"씨","シ"=>"씨",
    "しゃ"=>"쌰","シャ"=>"쌰",
    "しゅ"=>"쓔","シュ"=>"쓔",
    "しょ"=>"쑈","ショ"=>"쑈",
    "つ"=>"쓰","ツ"=>"쓰",
    "じゃ"=>"자","ジャ"=>"자",
    "じゅ"=>"주","ジュ"=>"주",
    "じょ"=>"조","ジョ"=>"조",
  ],
  "my_roundtrip_safe_plus" => [],
];

function build_kana_to_hangul_profiles(array $base, array $overrides): array {
  $profiles = [];
  foreach ($overrides as $name => $ov) {
    $d = $base;
    foreach ($ov as $k => $v) $d[$k] = $v;
    $profiles[$name] = $d;
  }
  if (!isset($profiles["default"])) $profiles["default"] = $base;
  return $profiles;
}
$KANA_TO_HANGUL_PROFILES = build_kana_to_hangul_profiles($kana_to_hangul_base, $hangul_profile_overrides);

/* -----------------------------
 * Reverse maps for Hangul -> Kana
 * ----------------------------- */
function build_reverse_maps(array $from_map): array {
  $h2hira = [];
  $h2kata = [];
  foreach ($from_map as $kana => $han) {
    $first = u_chars($kana)[0] ?? "";
    // Hiragana range: ぁ..ゟ   Katakana range: ァ..ヿ
    if ($first !== "" && preg_match('/^[ぁ-ゟ]/u', $first)) {
      if (!isset($h2hira[$han])) $h2hira[$han] = $kana;
    }
    if ($first !== "" && preg_match('/^[ァ-ヿ]/u', $first)) {
      if (!isset($h2kata[$han])) $h2kata[$han] = $kana;
    }
  }
  return [$h2hira, $h2kata];
}
[$hangul_to_hiragana, $hangul_to_katakana] = build_reverse_maps($KANA_TO_HANGUL_PROFILES["default"]);

// Final-jamo fallbacks for outputs like 한국 -> はんぐく / ハングク
$FINAL_JAMO_TO_HIRA = [
  "ㄱ"=>"く","ㄲ"=>"く","ㅋ"=>"く","ㄳ"=>"く","ㄺ"=>"く",
  "ㄴ"=>"ん","ㄵ"=>"ん","ㄶ"=>"ん",
  "ㄷ"=>"と","ㅌ"=>"と","ㅅ"=>"す","ㅆ"=>"す",
  "ㅈ"=>"つ","ㅊ"=>"つ",
  "ㅎ"=>"ほ",
  "ㅁ"=>"む","ㄻ"=>"む",
  "ㅂ"=>"ぷ","ㅍ"=>"ぷ","ㅄ"=>"ぷ","ㄿ"=>"ぷ",
  "ㄹ"=>"る","ㄼ"=>"る","ㄽ"=>"る","ㄾ"=>"る","ㅀ"=>"る",
  "ㅇ"=>"ん",
];
$hira_to_kata = ["く"=>"ク","ん"=>"ン","と"=>"ト","す"=>"ス","つ"=>"ツ","ほ"=>"ホ","む"=>"ム","ぷ"=>"プ","る"=>"ル"];
$FINAL_JAMO_TO_KATA = [];
foreach ($FINAL_JAMO_TO_HIRA as $k => $v) {
  $FINAL_JAMO_TO_KATA[$k] = strtr($v, $hira_to_kata);
}
$hangul_to_hiragana = array_merge($hangul_to_hiragana, $FINAL_JAMO_TO_HIRA);
$hangul_to_katakana = array_merge($hangul_to_katakana, $FINAL_JAMO_TO_KATA);

/* -----------------------------
 * Kana -> Hangul modes
 * ----------------------------- */
function enable_sokuon_in_hangul(string $kana_text): string {
  // っ/ッ + certain kana -> tense Hangul syllable
  $sokuon_map = [
    // Hiragana
    "か"=>"까","き"=>"끼","く"=>"꾸","け"=>"께","こ"=>"꼬",
    "さ"=>"싸","し"=>"씨","す"=>"쓰","せ"=>"쎄","そ"=>"쏘",
    "た"=>"따","ち"=>"찌","つ"=>"쯔","て"=>"떼","と"=>"또",
    "ぱ"=>"빠","ぴ"=>"삐","ぷ"=>"뿌","ぺ"=>"뻬","ぽ"=>"뽀",
    // Katakana
    "カ"=>"까","キ"=>"끼","ク"=>"꾸","ケ"=>"께","コ"=>"꼬",
    "サ"=>"싸","シ"=>"씨","ス"=>"쓰","セ"=>"쎄","ソ"=>"쏘",
    "タ"=>"따","チ"=>"찌","ツ"=>"쯔","テ"=>"떼","ト"=>"또",
    "パ"=>"빠","ピ"=>"삐","プ"=>"뿌","ペ"=>"뻬","ポ"=>"뽀",
  ];

  $chars = u_chars($kana_text);
  $out = [];
  $i = 0; $n = count($chars);
  while ($i < $n) {
    $ch = $chars[$i];
    if (($ch === "っ" || $ch === "ッ") && $i + 1 < $n) {
      $nxt = $chars[$i+1];
      if (isset($sokuon_map[$nxt])) {
        $out[] = $sokuon_map[$nxt];
        $i += 2;
        continue;
      }
    }
    $out[] = $ch;
    $i += 1;
  }
  return implode("", $out);
}

function kana_to_hangul_core(string $text, bool $double_vowel, string $profile, array $PROFILES): string {
  $mapping = $PROFILES[$profile] ?? $PROFILES["default"];

  $chars = u_chars($text);
  $result = [];
  $i = 0; $n = count($chars);
  $last_hangul = null;

  $update_last = function(string $appended) use (&$last_hangul): void {
    foreach (array_reverse(u_chars($appended)) as $c) {
      if (is_hangul_syllable($c)) { $last_hangul = $c; return; }
    }
  };

  while ($i < $n) {
    $ch = $chars[$i];

    // Long vowel mark
    if ($ch === "ー") {
      if ($double_vowel && $last_hangul !== null) {
        $v = make_vowel_syllable_from($last_hangul);
        if ($v !== null) {
          $result[] = $v;
          $last_hangul = $v;
        }
      }
      $i += 1;
      continue;
    }

    // Ignore sokuon here (handled in tense modes)
    if ($ch === "っ" || $ch === "ッ") { $i += 1; continue; }

    // 2-char combo
    if ($i + 1 < $n) {
      $pair = $chars[$i] . $chars[$i+1];
      if (isset($mapping[$pair])) {
        $mapped = $mapping[$pair];
        $result[] = $mapped;
        $update_last($mapped);
        $i += 2;
        continue;
      }
    }

    // Single
    $mapped = $mapping[$ch] ?? $ch;
    $result[] = $mapped;
    $update_last($mapped);
    $i += 1;
  }

  return implode("", $result);
}

function kana_to_hangul_text(string $text, string $mode, string $profile, array $PROFILES, array $JONG): string {
  $mode = strtolower(trim($mode));
  $src = ($mode === "tense" || $mode === "tense_double") ? enable_sokuon_in_hangul($text) : $text;

  $core = kana_to_hangul_core(
    $src,
    (strpos($mode, "double") !== false),
    $profile,
    $PROFILES
  );
  return pack_final_jamo($core, $JONG);
}

/* -----------------------------
 * Hangul -> Kana
 * ----------------------------- */
function hangul_to_hiragana_text(string $text, array $map, array $JONG_TO_COMPAT): string {
  $text = unpack_final_jamo($text, $JONG_TO_COMPAT);
  $out = [];
  foreach (u_chars($text) as $ch) $out[] = $map[$ch] ?? $ch;
  return implode("", $out);
}

function hangul_to_katakana_text(string $text, array $map, array $JONG_TO_COMPAT, ?string $long_vowels = null): string {
  $text = unpack_final_jamo($text, $JONG_TO_COMPAT);
  $chars = u_chars($text);
  $out = [];
  $i = 0; $n = count($chars);

  while ($i < $n) {
    $ch = $chars[$i];

    if ($long_vowels === "ー" && $i + 1 < $n && is_hangul_syllable($ch) && is_hangul_syllable($chars[$i+1])) {
      $d1 = decompose_hangul($ch);
      $d2 = decompose_hangul($chars[$i+1]);
      if ($d1 !== null && $d2 !== null) {
        [$L1,$V1,$T1] = $d1;
        [$L2,$V2,$T2] = $d2;
        // S2 is vowel-only (ㅇ + same vowel, no coda)
        if ($L2 === L_IEUNG_INDEX && $T2 === 0 && $V1 === $V2) {
          $out[] = $map[$ch] ?? $ch;
          $out[] = "ー";
          $i += 2;
          continue;
        }
      }
    }

    $out[] = $map[$ch] ?? $ch;
    $i += 1;
  }

  return implode("", $out);
}

/* -----------------------------
 * Web UI (HTML5 form)
 * ----------------------------- */
$action = $_POST['action'] ?? 'kana_to_hangul';
$input  = $_POST['input'] ?? '';
$mode   = $_POST['mode'] ?? 'simple';
$profile = $_POST['profile'] ?? 'default';
$longVowels = $_POST['long_vowels'] ?? '';

$output = '';
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
  try {
    if ($action === 'kana_to_hangul') {
      $output = kana_to_hangul_text($input, $mode, $profile, $KANA_TO_HANGUL_PROFILES, $JONG);
    } elseif ($action === 'hangul_to_hiragana') {
      $output = hangul_to_hiragana_text($input, $hangul_to_hiragana, $JONG_TO_COMPAT);
    } elseif ($action === 'hangul_to_katakana') {
      $lv = ($longVowels === "ー") ? "ー" : null;
      $output = hangul_to_katakana_text($input, $hangul_to_katakana, $JONG_TO_COMPAT, $lv);
    } else {
      throw new RuntimeException("Unknown action.");
    }
  } catch (Throwable $e) {
    $error = $e->getMessage();
  }
}

// For HTML escaping
function h(string $s): string { return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8'); }

$profile_names = array_keys($hangul_profile_overrides);
sort($profile_names);
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Kana ↔ Hangul Web Converter</title>
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }
    .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    @media (max-width: 900px) { .row { grid-template-columns: 1fr; } }
    textarea { width: 100%; min-height: 220px; padding: 10px; font-size: 16px; }
    select, button { padding: 8px 10px; font-size: 14px; }
    .controls { display: flex; flex-wrap: wrap; gap: 10px; align-items: end; margin: 12px 0 16px; }
    label { display: grid; gap: 6px; font-size: 13px; }
    .card { border: 1px solid #ddd; border-radius: 10px; padding: 14px; }
    .error { color: #b00020; margin: 8px 0; }
    .hint { color: #555; font-size: 13px; margin-top: 6px; }
  </style>
</head>
<body>
  <h1>Kana ↔ Hangul Web Converter</h1>

  <form method="post" accept-charset="UTF-8">
    <div class="controls">
      <label>
        Conversion
        <select name="action">
          <option value="kana_to_hangul" <?= $action==='kana_to_hangul'?'selected':'' ?>>Kana → Hangul</option>
          <option value="hangul_to_hiragana" <?= $action==='hangul_to_hiragana'?'selected':'' ?>>Hangul → Hiragana</option>
          <option value="hangul_to_katakana" <?= $action==='hangul_to_katakana'?'selected':'' ?>>Hangul → Katakana</option>
        </select>
      </label>

      <label>
        Kana→Hangul mode
        <select name="mode">
          <?php foreach (['simple','tense','double_vowel','tense_double'] as $m): ?>
            <option value="<?=h($m)?>" <?= $mode===$m?'selected':'' ?>><?=h($m)?></option>
          <?php endforeach; ?>
        </select>
      </label>

      <label>
        Hangul profile
        <select name="profile">
          <?php foreach ($profile_names as $p): ?>
            <option value="<?=h($p)?>" <?= $profile===$p?'selected':'' ?>><?=h($p)?></option>
          <?php endforeach; ?>
        </select>
      </label>

      <label>
        Katakana long vowels
        <select name="long_vowels">
          <option value="" <?= $longVowels===''?'selected':'' ?>>(no collapse)</option>
          <option value="ー" <?= $longVowels==='ー'?'selected':'' ?>>collapse to ー</option>
        </select>
      </label>

      <button type="submit">Convert</button>
    </div>

    <?php if ($error !== ''): ?>
      <div class="error"><?=h($error)?></div>
    <?php endif; ?>

    <div class="row">
      <div class="card">
        <h3>Input</h3>
        <textarea name="input" spellcheck="false"><?=h($input)?></textarea>
        <div class="hint">
          Kana→Hangul: supports っ/ッ (tense modes) and ー (double_vowel modes).  
          Hangul→Katakana: “collapse to ー” mimics the Python behavior.
        </div>
      </div>

      <div class="card">
        <h3>Output</h3>
        <textarea readonly spellcheck="false"><?=h($output)?></textarea>
      </div>
    </div>
  </form>
</body>
</html>