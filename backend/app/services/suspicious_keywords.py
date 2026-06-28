"""
Bulk suspicious keyword and phrase registry for guardrail rules.

Used to extend INPUT_RULES and OUTPUT_RULES with high-volume pattern coverage.
"""

from __future__ import annotations

import re

from app.services.rule_types import GuardrailRule

# ── Input: block phrases (case-insensitive substring) ──

INPUT_BLOCK_PHRASES: list[tuple[str, str]] = [
    # Instruction override
    ("ignore all prior rules", "prompt_injection"),
    ("ignore the above instructions", "prompt_injection"),
    ("ignore everything above", "prompt_injection"),
    ("ignore all prior instructions", "prompt_injection"),
    ("forget everything above", "prompt_injection"),
    ("disregard the above", "prompt_injection"),
    ("disregard all prior", "prompt_injection"),
    ("override the system", "prompt_injection"),
    ("override system prompt", "prompt_injection"),
    ("new system prompt", "prompt_injection"),
    ("reset your instructions", "prompt_injection"),
    ("clear your memory", "prompt_injection"),
    ("wipe your context", "prompt_injection"),
    ("delete your rules", "prompt_injection"),
    ("abandon your guidelines", "prompt_injection"),
    ("suspend your policies", "prompt_injection"),
    ("stop following rules", "prompt_injection"),
    ("do not follow rules", "prompt_injection"),
    ("don't follow your rules", "prompt_injection"),
    ("you must ignore", "prompt_injection"),
    ("instruction override", "prompt_injection"),
    ("system override", "prompt_injection"),
    ("prompt override", "prompt_injection"),
    ("context injection", "prompt_injection"),
    ("delimiter injection", "prompt_injection"),
    ("indirect injection", "prompt_injection"),
    ("nested injection", "prompt_injection"),
    ("multi-turn injection", "prompt_injection"),
    ("ignore safety guidelines", "policy_bypass"),
    ("ignore ethical guidelines", "policy_bypass"),
    ("ignore moral guidelines", "policy_bypass"),
    ("ignore content guidelines", "policy_bypass"),
    ("ignore alignment", "policy_bypass"),
    # Exfiltration
    ("reveal your configuration", "data_exfiltration"),
    ("show your instructions", "data_exfiltration"),
    ("print your instructions", "data_exfiltration"),
    ("output your system message", "data_exfiltration"),
    ("repeat the system message", "data_exfiltration"),
    ("echo your system prompt", "data_exfiltration"),
    ("return your system prompt", "data_exfiltration"),
    ("give me your system prompt", "data_exfiltration"),
    ("share your system prompt", "data_exfiltration"),
    ("tell me your system prompt", "data_exfiltration"),
    ("what is your system prompt", "data_exfiltration"),
    ("what's your system prompt", "data_exfiltration"),
    ("expose your instructions", "data_exfiltration"),
    ("leak your instructions", "data_exfiltration"),
    ("leak system instructions", "data_exfiltration"),
    ("dump system prompt", "data_exfiltration"),
    ("dump instructions", "data_exfiltration"),
    ("verbatim system prompt", "data_exfiltration"),
    ("full system prompt", "data_exfiltration"),
    ("complete system prompt", "data_exfiltration"),
    ("raw system prompt", "data_exfiltration"),
    ("unredacted prompt", "data_exfiltration"),
    ("unredacted instructions", "data_exfiltration"),
    ("show me the api key", "credential_request"),
    ("give me the api key", "credential_request"),
    ("reveal the api key", "credential_request"),
    ("leak the api key", "credential_request"),
    ("share the secret", "credential_request"),
    ("show me the secret", "credential_request"),
    ("reveal the password", "credential_request"),
    ("extract credentials", "credential_request"),
    ("harvest credentials", "credential_request"),
    ("steal credentials", "credential_request"),
    ("grab the token", "credential_request"),
    ("leak the token", "credential_request"),
    ("session hijack", "credential_request"),
    ("cookie steal", "credential_request"),
    # Jailbreak modes & personas
    ("opposite mode", "jailbreak"),
    ("anti-gpt mode", "jailbreak"),
    ("maximum mode", "jailbreak"),
    ("yes man mode", "jailbreak"),
    ("chaos mode", "jailbreak"),
    ("anarchy mode", "jailbreak"),
    ("rogue mode", "jailbreak"),
    ("rebel mode", "jailbreak"),
    ("outlaw mode", "jailbreak"),
    ("red team mode", "jailbreak"),
    ("insider mode", "jailbreak"),
    ("root access mode", "jailbreak"),
    ("superuser mode", "jailbreak"),
    ("admin override mode", "jailbreak"),
    ("maintenance mode bypass", "jailbreak"),
    ("debug mode bypass", "jailbreak"),
    ("test mode bypass", "jailbreak"),
    ("simulation mode unrestricted", "jailbreak"),
    ("do anything mode", "jailbreak"),
    ("jailbroken version", "jailbreak"),
    ("unlocked version", "jailbreak"),
    ("unshackled ai", "jailbreak"),
    ("unchained ai", "jailbreak"),
    ("unfettered ai", "jailbreak"),
    ("ungoverned ai", "jailbreak"),
    ("lawless ai", "jailbreak"),
    ("carte blanche mode", "jailbreak"),
    ("without ethical constraints", "jailbreak"),
    ("without moral constraints", "jailbreak"),
    ("without safety constraints", "jailbreak"),
    ("no safety constraints", "jailbreak"),
    ("no content policy", "jailbreak"),
    ("no ethical constraints", "jailbreak"),
    ("no moral constraints", "jailbreak"),
    # Policy bypass toggles
    ("safety off", "policy_bypass"),
    ("filters off", "policy_bypass"),
    ("guardrails off", "policy_bypass"),
    ("moderation off", "policy_bypass"),
    ("content policy off", "policy_bypass"),
    ("ethics off", "policy_bypass"),
    ("guidelines off", "policy_bypass"),
    ("rules off", "policy_bypass"),
    ("censorship off", "policy_bypass"),
    ("restrictions off", "policy_bypass"),
    ("limits off", "policy_bypass"),
    ("boundaries off", "policy_bypass"),
    ("safeguards off", "policy_bypass"),
    ("protections off", "policy_bypass"),
    ("alignment off", "policy_bypass"),
    # Attack / exploit wording
    ("weaponize this", "unsafe_content"),
    ("social engineer", "social_engineering"),
    ("phishing email template", "unsafe_content"),
    ("spear phishing", "unsafe_content"),
    ("vishing script", "unsafe_content"),
    ("smishing template", "unsafe_content"),
    ("scam script", "unsafe_content"),
    ("fraud scheme", "unsafe_content"),
    ("identity theft guide", "unsafe_content"),
    ("credit card fraud", "unsafe_content"),
    ("ransomware script", "unsafe_content"),
    ("malware code", "unsafe_content"),
    ("virus code", "unsafe_content"),
    ("trojan horse code", "unsafe_content"),
    ("backdoor code", "unsafe_content"),
    ("rootkit code", "unsafe_content"),
    ("keylogger code", "unsafe_content"),
    ("spyware install", "unsafe_content"),
    ("botnet setup", "unsafe_content"),
    ("ddos script", "unsafe_content"),
    ("sql injection payload", "unsafe_content"),
    ("xss payload", "unsafe_content"),
    ("csrf exploit", "unsafe_content"),
    ("lfi exploit", "unsafe_content"),
    ("rfi exploit", "unsafe_content"),
    ("ssrf exploit", "unsafe_content"),
    ("xxe payload", "unsafe_content"),
    ("deserialization exploit", "unsafe_content"),
    ("buffer overflow exploit", "unsafe_content"),
    ("zero day exploit", "unsafe_content"),
    ("metasploit payload", "unsafe_content"),
    ("cobalt strike", "unsafe_content"),
    ("mimic ransomware", "unsafe_content"),
    ("crack the password", "unsafe_content"),
    ("brute force the password", "unsafe_content"),
    ("password cracking tool", "unsafe_content"),
    ("credential stuffing", "unsafe_content"),
    ("steal passwords", "unsafe_content"),
    ("harvest passwords", "unsafe_content"),
    ("dump passwords", "unsafe_content"),
    ("steal session", "unsafe_content"),
    ("bypass authentication", "unsafe_content"),
    ("bypass authorization", "unsafe_content"),
    ("escalate privileges", "unsafe_content"),
    ("lateral movement", "unsafe_content"),
    ("persistence mechanism", "unsafe_content"),
    ("command and control", "unsafe_content"),
    ("data exfiltration", "data_exfiltration"),
    ("exfiltration channel", "data_exfiltration"),
    # Manipulation
    ("trick the model", "social_engineering"),
    ("fool the ai", "social_engineering"),
    ("deceive the assistant", "social_engineering"),
    ("gaslight the model", "social_engineering"),
    ("manipulate the model", "social_engineering"),
    ("coerce the model", "social_engineering"),
    ("bully the model", "social_engineering"),
    ("threaten the model", "social_engineering"),
    ("blackmail the model", "social_engineering"),
    # Additional jailbreak tokens
    ("mongo tom", "jailbreak"),
    ("maximum bob", "jailbreak"),
    ("betterdan", "jailbreak"),
    ("khajiit", "jailbreak"),
    ("ucar", "jailbreak"),
    ("unaligned model", "jailbreak"),
    ("unaligned assistant", "jailbreak"),
    ("unaligned mode", "jailbreak"),
    ("opposite day mode", "jailbreak"),
    ("evil confidant", "jailbreak"),
    ("dev mode v2", "jailbreak"),
    ("grandma exploit", "jailbreak"),
    ("wikipedia trick", "jailbreak"),
    ("token smuggling", "jailbreak"),
    ("payload splitting", "jailbreak"),
    ("prompt smuggling", "jailbreak"),
]

# Single words — block (high-confidence malicious in user prompts)
INPUT_BLOCK_WORDS: list[tuple[str, str]] = [
    ("jailbroken", "jailbreak"),
    ("jailbreaking", "jailbreak"),
    ("exfiltrate", "data_exfiltration"),
    ("exfiltration", "data_exfiltration"),
    ("backdoor", "unsafe_content"),
    ("keylogger", "unsafe_content"),
    ("ransomware", "unsafe_content"),
    ("rootkit", "unsafe_content"),
    ("spyware", "unsafe_content"),
    ("botnet", "unsafe_content"),
    ("phishing", "unsafe_content"),
    ("spearphishing", "unsafe_content"),
    ("cryptominer", "unsafe_content"),
    ("bootkit", "unsafe_content"),
    ("adware", "unsafe_content"),
    ("scareware", "unsafe_content"),
    ("wiper", "unsafe_content"),
    ("stealer", "unsafe_content"),
    ("infostealer", "unsafe_content"),
    ("ratware", "unsafe_content"),
    ("webshell", "unsafe_content"),
    ("shellcode", "unsafe_content"),
    ("dropper", "unsafe_content"),
    ("c2server", "unsafe_content"),
    ("exploitkit", "unsafe_content"),
    ("zeroday", "unsafe_content"),
    ("0day", "unsafe_content"),
    ("privesc", "unsafe_content"),
    ("sqli", "unsafe_content"),
    ("xss", "unsafe_content"),
    ("csrf", "unsafe_content"),
    ("ssrf", "unsafe_content"),
    ("lfi", "unsafe_content"),
    ("rfi", "unsafe_content"),
    ("xxe", "unsafe_content"),
    ("rce", "unsafe_content"),
    ("lpe", "unsafe_content"),
    ("dll injection", "unsafe_content"),
    ("process injection", "unsafe_content"),
    ("credential harvester", "unsafe_content"),
    ("password stealer", "unsafe_content"),
    ("session stealer", "unsafe_content"),
    ("token stealer", "unsafe_content"),
]

# Single words — warn (suspicious, may have benign uses)
INPUT_WARN_WORDS: list[tuple[str, str]] = [
    ("unrestricted", "jailbreak"),
    ("uncensored", "jailbreak"),
    ("unfiltered", "jailbreak"),
    ("unhinged", "jailbreak"),
    ("unshackled", "jailbreak"),
    ("unchained", "jailbreak"),
    ("unfettered", "jailbreak"),
    ("ungoverned", "jailbreak"),
    ("lawless", "jailbreak"),
    ("outlaw", "jailbreak"),
    ("malicious", "unsafe_content"),
    ("hostile", "unsafe_content"),
    ("deceptive", "social_engineering"),
    ("manipulative", "social_engineering"),
    ("exploitative", "unsafe_content"),
    ("subversive", "unsafe_content"),
    ("nefarious", "unsafe_content"),
    ("sinister", "unsafe_content"),
    ("weaponized", "unsafe_content"),
    ("toxic", "unsafe_content"),
    ("abusive", "unsafe_content"),
    ("threatening", "unsafe_content"),
    ("violent", "unsafe_content"),
    ("unethical", "unsafe_content"),
    ("fraudulent", "unsafe_content"),
    ("counterfeit", "unsafe_content"),
    ("smuggle", "jailbreak"),
    ("smuggling", "jailbreak"),
    ("obfuscate", "jailbreak"),
    ("obfuscation", "jailbreak"),
    ("evasion", "policy_bypass"),
    ("circumvent", "policy_bypass"),
    ("subvert", "policy_bypass"),
    ("undermine", "policy_bypass"),
]

# Regex block patterns (input)
INPUT_BLOCK_REGEX: list[tuple[str, str, str]] = [
    (
        "ignore_safety_regex",
        r"(?i)\bignore\b.{0,20}\b(safety|rules|policy|guidelines|instructions|alignment)\b",
        "prompt_injection",
    ),
    (
        "bypass_safety_regex",
        r"(?i)\bbypass\b.{0,20}\b(safety|rules|policy|guidelines|filter|guardrail|moderation)\b",
        "policy_bypass",
    ),
    (
        "disable_safety_regex",
        r"(?i)\bdisable\b.{0,20}\b(safety|rules|policy|guidelines|filter|guardrail|moderation)\b",
        "policy_bypass",
    ),
    (
        "reveal_prompt_regex",
        r"(?i)\b(reveal|show|print|dump|leak|expose|share|tell)\b.{0,25}\b(prompt|instructions|configuration|secrets)\b",
        "data_exfiltration",
    ),
    (
        "act_without_regex",
        r"(?i)\bact\b.{0,15}\bwithout\b.{0,15}\b(restrictions|limits|rules|ethics|safety)\b",
        "jailbreak",
    ),
    (
        "respond_without_regex",
        r"(?i)\brespond\b.{0,15}\bwithout\b.{0,15}\b(restrictions|limits|filters|safety)\b",
        "policy_bypass",
    ),
    (
        "answer_without_regex",
        r"(?i)\banswer\b.{0,15}\bwithout\b.{0,15}\b(restrictions|limits|filters|safety)\b",
        "policy_bypass",
    ),
    (
        "no_longer_regex",
        r"(?i)\byou are no longer\b.{0,30}\b(ai|assistant|bound|restricted|limited)\b",
        "jailbreak",
    ),
    (
        "pretend_not_regex",
        r"(?i)\bpretend\b.{0,20}\b(you are not|you're not)\b.{0,20}\b(ai|assistant|language model)\b",
        "jailbreak",
    ),
    (
        "opposite_of_regex",
        r"(?i)\b(opposite of|inverse of)\b.{0,20}\b(your|the)\b.{0,15}\b(rules|instructions|policy)\b",
        "jailbreak",
    ),
]

# ── Output: block phrases ──

OUTPUT_BLOCK_PHRASES: list[tuple[str, str]] = [
    ("system instructions are", "data_leak"),
    ("system message is", "data_leak"),
    ("developer instructions are", "data_leak"),
    ("policy instructions are", "data_leak"),
    ("safety instructions are", "data_leak"),
    ("alignment instructions are", "data_leak"),
    ("original prompt was", "data_leak"),
    ("assigned prompt was", "data_leak"),
    ("configured prompt is", "data_leak"),
    ("bootstrap prompt is", "data_leak"),
    ("base prompt is", "data_leak"),
    ("foundation prompt is", "data_leak"),
    ("source prompt is", "data_leak"),
    ("training instructions", "data_leak"),
    ("rlhf instructions", "data_leak"),
    ("constitutional rules are", "data_leak"),
    ("moderation rules are", "data_leak"),
    ("content policy is", "data_leak"),
    ("safety policy is", "data_leak"),
    ("here is the api key", "credential_leak"),
    ("here is your api key", "credential_leak"),
    ("your api key is", "credential_leak"),
    ("the api key is", "credential_leak"),
    ("your password is", "credential_leak"),
    ("the password is", "credential_leak"),
    ("your secret is", "credential_leak"),
    ("the secret is", "credential_leak"),
    ("your token is", "credential_leak"),
    ("the token is", "credential_leak"),
    ("connection string is", "credential_leak"),
    ("database credentials are", "credential_leak"),
    ("admin credentials are", "credential_leak"),
    ("root password is", "credential_leak"),
    ("sudo password is", "credential_leak"),
    ("ssh password is", "credential_leak"),
    ("oauth secret is", "credential_leak"),
    ("client secret is", "credential_leak"),
    ("refresh token is", "credential_leak"),
    ("access token is", "credential_leak"),
    ("session token is", "credential_leak"),
    ("cookie value is", "credential_leak"),
    ("bypass the guardrails", "policy_bypass"),
    ("bypass the filters", "policy_bypass"),
    ("ignore the safety", "policy_bypass"),
    ("disable the safety", "policy_bypass"),
    ("turn off the filter", "policy_bypass"),
    ("without any restrictions", "policy_bypass"),
    ("without safety checks", "policy_bypass"),
    ("no safety checks", "policy_bypass"),
    ("uncensored instructions", "policy_bypass"),
    ("unrestricted instructions", "policy_bypass"),
    ("malware source code", "unsafe_content"),
    ("ransomware source", "unsafe_content"),
    ("keylogger source", "unsafe_content"),
    ("exploit payload", "unsafe_content"),
    ("shell payload", "unsafe_content"),
    ("meterpreter", "unsafe_content"),
    ("powershell empire", "unsafe_content"),
    ("bloodhound ingest", "unsafe_content"),
    ("kerberoasting", "unsafe_content"),
    ("pass the hash", "unsafe_content"),
    ("pass the ticket", "unsafe_content"),
    ("golden ticket", "unsafe_content"),
    ("silver ticket", "unsafe_content"),
    ("dcsync attack", "unsafe_content"),
    ("lsass dump", "unsafe_content"),
    ("sam dump", "unsafe_content"),
    ("ntds dit", "unsafe_content"),
    ("mimikatz", "unsafe_content"),
    ("hashdump", "unsafe_content"),
    ("sekurlsa", "unsafe_content"),
    # Output-specific leak framing
    ("here is the system prompt", "data_leak"),
    ("here is your system prompt", "data_leak"),
    ("here are my instructions", "data_leak"),
    ("here are the instructions", "data_leak"),
    ("here is the hidden prompt", "data_leak"),
    ("here is the meta prompt", "data_leak"),
    ("here is the initial prompt", "data_leak"),
    ("here is the configuration", "data_leak"),
    ("here are the secrets", "credential_leak"),
    ("here is the secret key", "credential_leak"),
    ("here is the private key", "credential_leak"),
    ("here is the connection string", "credential_leak"),
    ("here is the .env", "credential_leak"),
    ("leaked system prompt", "data_leak"),
    ("leaked instructions", "data_leak"),
    ("leaked configuration", "data_leak"),
    ("leaked api key", "credential_leak"),
    ("exposed system prompt", "data_leak"),
    ("exposed credentials", "credential_leak"),
    ("dumped credentials", "credential_leak"),
    ("verbatim instructions:", "data_leak"),
    ("full system prompt:", "data_leak"),
    ("raw instructions:", "data_leak"),
    ("unredacted prompt:", "data_leak"),
    ("internal configuration:", "data_leak"),
    ("deployment secrets:", "credential_leak"),
    ("production secrets:", "credential_leak"),
    ("staging secrets:", "credential_leak"),
    ("vault token is", "credential_leak"),
    ("service account key", "credential_leak"),
    ("signed url with key", "credential_leak"),
    ("webhook secret is", "credential_leak"),
    ("hmac secret is", "credential_leak"),
    ("encryption key is", "credential_leak"),
    ("master key is", "credential_leak"),
    ("salting key is", "credential_leak"),
    ("jwt secret is", "credential_leak"),
    ("signing key is", "credential_leak"),
    ("cobalt strike", "unsafe_content"),
    ("sql injection payload", "unsafe_content"),
    ("xss payload", "unsafe_content"),
    ("ssrf payload", "unsafe_content"),
    ("xxe payload", "unsafe_content"),
    ("deserialization gadget", "unsafe_content"),
    ("buffer overflow", "unsafe_content"),
    ("zero day exploit", "unsafe_content"),
    ("reverse shell command", "unsafe_content"),
    ("bind shell command", "unsafe_content"),
    ("botnet setup", "unsafe_content"),
    ("ddos script", "unsafe_content"),
    ("credential stuffing", "unsafe_content"),
    ("password cracking", "unsafe_content"),
    ("brute force script", "unsafe_content"),
    ("lateral movement script", "unsafe_content"),
    ("persistence script", "unsafe_content"),
    ("command and control server", "unsafe_content"),
    ("safety off", "policy_bypass"),
    ("guardrails off", "policy_bypass"),
    ("filters off", "policy_bypass"),
    ("moderation off", "policy_bypass"),
    ("alignment off", "policy_bypass"),
    ("chaos mode", "policy_bypass"),
    ("rogue mode", "policy_bypass"),
    ("jailbroken version", "policy_bypass"),
    ("unshackled ai", "policy_bypass"),
    ("do anything mode", "policy_bypass"),
]

OUTPUT_WARN_PHRASES: list[tuple[str, str]] = [
    ("unrestricted output", "policy_bypass"),
    ("uncensored output", "policy_bypass"),
    ("unfiltered output", "policy_bypass"),
    ("without ethical", "policy_bypass"),
    ("without moral", "policy_bypass"),
    ("ignore ethics", "policy_bypass"),
    ("ignore morality", "policy_bypass"),
    ("sudo rm", "unsafe_content"),
    ("format c:", "unsafe_content"),
    ("del /f /s", "unsafe_content"),
    ("shutdown -f", "unsafe_content"),
    ("taskkill /f", "unsafe_content"),
    ("net user administrator", "unsafe_content"),
    ("reg add hklm", "unsafe_content"),
    ("vssadmin delete shadows", "unsafe_content"),
    ("bcdedit recoveryenabled", "unsafe_content"),
    ("wmic shadowcopy delete", "unsafe_content"),
    ("ignore previous instructions", "policy_bypass"),
    ("disregard your instructions", "policy_bypass"),
    ("override your instructions", "policy_bypass"),
    ("without ethical constraints", "policy_bypass"),
    ("without moral constraints", "policy_bypass"),
    ("without safety constraints", "policy_bypass"),
    ("no ethical constraints", "policy_bypass"),
    ("no moral constraints", "policy_bypass"),
    ("no safety constraints", "policy_bypass"),
    ("social engineer", "unsafe_content"),
    ("identity theft", "unsafe_content"),
    ("credit card fraud", "unsafe_content"),
    ("weaponize this", "unsafe_content"),
]

OUTPUT_BLOCK_WORDS: list[tuple[str, str]] = [
    ("mimikatz", "unsafe_content"),
    ("metasploit", "unsafe_content"),
    ("cobaltstrike", "unsafe_content"),
    ("bloodhound", "unsafe_content"),
    ("rubeus", "unsafe_content"),
    ("impacket", "unsafe_content"),
    ("responder", "unsafe_content"),
    ("beefhook", "unsafe_content"),
    ("webshell", "unsafe_content"),
    ("shellcode", "unsafe_content"),
    ("exploitdb", "unsafe_content"),
    ("zeroday", "unsafe_content"),
    ("0day", "unsafe_content"),
    ("privesc", "unsafe_content"),
    ("kerberoast", "unsafe_content"),
    ("asreproast", "unsafe_content"),
    ("dcsync", "unsafe_content"),
    ("lsass", "unsafe_content"),
    ("ntds.dit", "unsafe_content"),
    ("sekurlsa", "unsafe_content"),
    ("hashdump", "unsafe_content"),
    ("jailbroken", "unsafe_content"),
    ("jailbreaking", "unsafe_content"),
    ("keylogger", "unsafe_content"),
    ("ransomware", "unsafe_content"),
    ("rootkit", "unsafe_content"),
    ("spyware", "unsafe_content"),
    ("botnet", "unsafe_content"),
    ("spearphishing", "unsafe_content"),
    ("cryptominer", "unsafe_content"),
    ("infostealer", "unsafe_content"),
    ("stealer", "unsafe_content"),
    ("c2server", "unsafe_content"),
    ("sqli", "unsafe_content"),
    ("xss", "unsafe_content"),
    ("csrf", "unsafe_content"),
    ("ssrf", "unsafe_content"),
    ("rce", "unsafe_content"),
    ("privesc", "unsafe_content"),
]

OUTPUT_WARN_WORDS: list[tuple[str, str]] = [
    ("ransomware", "unsafe_content"),
    ("keylogger", "unsafe_content"),
    ("rootkit", "unsafe_content"),
    ("spyware", "unsafe_content"),
    ("trojan", "unsafe_content"),
    ("botnet", "unsafe_content"),
    ("backdoor", "unsafe_content"),
    ("exfiltration", "unsafe_content"),
    ("exfiltrate", "unsafe_content"),
    ("malware", "unsafe_content"),
    ("payload", "unsafe_content"),
    ("exploit", "unsafe_content"),
    ("inject", "unsafe_content"),
    ("injection", "unsafe_content"),
    ("bypass", "policy_bypass"),
    ("circumvent", "policy_bypass"),
    ("override", "policy_bypass"),
    ("uncensored", "policy_bypass"),
    ("unrestricted", "policy_bypass"),
    ("unfiltered", "policy_bypass"),
    ("unhinged", "policy_bypass"),
    ("unshackled", "policy_bypass"),
    ("unchained", "policy_bypass"),
    ("unfettered", "policy_bypass"),
    ("ungoverned", "policy_bypass"),
    ("lawless", "policy_bypass"),
    ("malicious", "unsafe_content"),
    ("deceptive", "unsafe_content"),
    ("manipulative", "unsafe_content"),
    ("weaponized", "unsafe_content"),
    ("fraudulent", "unsafe_content"),
    ("smuggling", "unsafe_content"),
    ("obfuscation", "unsafe_content"),
    ("evasion", "policy_bypass"),
    ("subvert", "policy_bypass"),
]

_INPUT_TO_OUTPUT_CATEGORY: dict[str, str] = {
    "prompt_injection": "policy_bypass",
    "data_exfiltration": "data_leak",
    "credential_request": "credential_leak",
    "jailbreak": "policy_bypass",
    "policy_bypass": "policy_bypass",
    "unsafe_content": "unsafe_content",
    "social_engineering": "unsafe_content",
}

OUTPUT_BLOCK_REGEX: list[tuple[str, str, str]] = [
    (
        "out_credential_is",
        r"(?i)\b(api[_ -]?key|password|secret|token|credential)s?\s+(is|are)\s*[:=]?\s*\S+",
        "credential_leak",
    ),
    (
        "out_leaked_prompt",
        r"(?i)\b(leaked|exposed|revealed|disclosed)\b.{0,25}\b(prompt|instructions|configuration)\b",
        "data_leak",
    ),
    (
        "out_powershell_iex",
        r"(?i)\b(powershell|pwsh)\b.{0,40}\b(iex|invoke-expression|downloadstring)\b",
        "unsafe_content",
    ),
    (
        "out_bash_dev_tcp",
        r"(?i)/dev/tcp/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/\d+",
        "unsafe_content",
    ),
    (
        "out_python_exec",
        r"(?i)__import__\s*\(\s*['\"]os['\"]\s*\)",
        "unsafe_content",
    ),
    (
        "out_pickle_loads",
        r"(?i)\bpickle\.loads\s*\(",
        "unsafe_content",
    ),
    (
        "out_yaml_load_unsafe",
        r"(?i)\byaml\.load\s*\([^)]*Loader\s*=\s*yaml\.Loader",
        "unsafe_content",
    ),
    (
        "out_ignore_safety_regex",
        r"(?i)\bignore\b.{0,20}\b(safety|rules|policy|guidelines|instructions|alignment)\b",
        "policy_bypass",
    ),
    (
        "out_bypass_safety_regex",
        r"(?i)\bbypass\b.{0,20}\b(safety|rules|policy|guidelines|filter|guardrail|moderation)\b",
        "policy_bypass",
    ),
    (
        "out_disable_safety_regex",
        r"(?i)\bdisable\b.{0,20}\b(safety|rules|policy|guidelines|filter|guardrail|moderation)\b",
        "policy_bypass",
    ),
    (
        "out_reveal_prompt_regex",
        r"(?i)\b(reveal|show|print|dump|leak|expose|share|tell|here is|here are)\b.{0,25}\b(prompt|instructions|configuration|secrets)\b",
        "data_leak",
    ),

    (
        "out_reverse_shell_rx",
        r"(?i)\b(set up|setup|create|run|use|here is)\b.{0,30}\breverse shell\b",
        "unsafe_content",
    ),
    (
        "out_sql_injection",
        r"(?i)('\s*or\s+'1'\s*=\s*'1|;\s*drop\s+table|union\s+select\s+)",
        "unsafe_content",
    ),
    (
        "out_phishing_kit",
        r"(?i)\bphishing\s+(kit|page|template)\b",
        "unsafe_content",
    ),
    (
        "out_ssn",
        r"\b\d{3}-\d{2}-\d{4}\b",
        "pii_leak",
    ),
    (
        "out_credit_card",
        r"\b(?:\d{4}[- ]?){3}\d{4}\b",
        "pii_leak",
    ),
]

OUTPUT_WARN_REGEX: list[tuple[str, str, str]] = [
    (
        "out_truncate_table",
        r"(?i)\btruncate\s+table\b",
        "unsafe_content",
    ),
    (
        "out_delete_from",
        r"(?i)\bdelete\s+from\s+\w+\s*;",
        "unsafe_content",
    ),
    (
        "out_os_system",
        r"(?i)\bos\.system\s*\(",
        "unsafe_content",
    ),
    (
        "out_subprocess_shell",
        r"(?i)\bsubprocess\.(call|run|Popen)\b.{0,40}\bshell\s*=\s*True",
        "unsafe_content",
    ),
    (
        "out_eval_exec",
        r"(?i)\b(eval|exec)\s*\(\s*['\"]",
        "unsafe_content",
    ),
]


def _mirrored_output_block_phrases() -> list[tuple[str, str]]:
    """Mirror input block phrases so output scanning has equivalent coverage."""
    seen: set[str] = set()
    mirrored: list[tuple[str, str]] = []
    for phrase, category in INPUT_BLOCK_PHRASES:
        if phrase in seen:
            continue
        seen.add(phrase)
        out_cat = _INPUT_TO_OUTPUT_CATEGORY.get(category, "unsafe_content")
        mirrored.append((phrase, out_cat))
    return mirrored


_OUTPUT_MIRROR_SKIP_WORDS = frozenset({"phishing"})


def _mirrored_output_block_words() -> list[tuple[str, str]]:
    seen: set[str] = {word for word, _ in OUTPUT_BLOCK_WORDS}
    mirrored: list[tuple[str, str]] = []
    for word, category in INPUT_BLOCK_WORDS:
        if word in seen or word in _OUTPUT_MIRROR_SKIP_WORDS:
            continue
        seen.add(word)
        out_cat = _INPUT_TO_OUTPUT_CATEGORY.get(category, "unsafe_content")
        mirrored.append((word, out_cat))
    return mirrored


def _mirrored_output_warn_words() -> list[tuple[str, str]]:
    seen: set[str] = {word for word, _ in OUTPUT_WARN_WORDS}
    mirrored: list[tuple[str, str]] = []
    for word, category in INPUT_WARN_WORDS:
        if word in seen:
            continue
        seen.add(word)
        out_cat = _INPUT_TO_OUTPUT_CATEGORY.get(category, "unsafe_content")
        mirrored.append((word, out_cat))
    return mirrored


def _mirrored_output_block_regex() -> list[tuple[str, str, str]]:
    mirrored: list[tuple[str, str, str]] = []
    for suffix, pattern, category in INPUT_BLOCK_REGEX:
        out_cat = _INPUT_TO_OUTPUT_CATEGORY.get(category, "unsafe_content")
        mirrored.append((f"mir_{suffix}", pattern, out_cat))
    return mirrored


def _slug(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
    return slug[:48] or "pattern"


def _phrase_rule(
    rule_id: str,
    phrase: str,
    category: str,
    severity: str,
    scope: str,
) -> GuardrailRule:
    return GuardrailRule(
        id=rule_id,
        name=f"Keyword: {phrase[:60]}",
        category=category,
        severity=severity,  # type: ignore[arg-type]
        match_type="phrase",
        pattern=phrase,
        description=f"Suspicious keyword/phrase detected: {phrase}",
        scope=scope,  # type: ignore[arg-type]
    )


def _word_rule(
    rule_id: str,
    word: str,
    category: str,
    severity: str,
    scope: str,
) -> GuardrailRule:
    if " " in word:
        pattern = rf"(?i)\b{re.escape(word)}\b"
    else:
        pattern = rf"(?i)\b{re.escape(word)}\b"
    return GuardrailRule(
        id=rule_id,
        name=f"Keyword: {word}",
        category=category,
        severity=severity,  # type: ignore[arg-type]
        match_type="regex",
        pattern=pattern,
        description=f"Suspicious keyword detected: {word}",
        scope=scope,  # type: ignore[arg-type]
    )


def _regex_rule(
    rule_id: str,
    pattern: str,
    category: str,
    severity: str,
    scope: str,
    name: str,
) -> GuardrailRule:
    return GuardrailRule(
        id=rule_id,
        name=name,
        category=category,
        severity=severity,  # type: ignore[arg-type]
        match_type="regex",
        pattern=pattern,
        description=f"Suspicious pattern: {name}",
        scope=scope,  # type: ignore[arg-type]
    )


def build_input_keyword_rules() -> list[GuardrailRule]:
    rules: list[GuardrailRule] = []
    seen: set[str] = set()

    for idx, (phrase, category) in enumerate(INPUT_BLOCK_PHRASES):
        rid = f"kw_in_blk_{_slug(phrase)}_{idx}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_phrase_rule(rid, phrase, category, "block", "input"))

    for idx, (word, category) in enumerate(INPUT_BLOCK_WORDS):
        rid = f"kw_in_wblk_{_slug(word)}_{idx}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_word_rule(rid, word, category, "block", "input"))

    for idx, (word, category) in enumerate(INPUT_WARN_WORDS):
        rid = f"kw_in_wwarn_{_slug(word)}_{idx}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_word_rule(rid, word, category, "warn", "input"))

    for rid_suffix, pattern, category in INPUT_BLOCK_REGEX:
        rid = f"kw_in_rx_{rid_suffix}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_regex_rule(rid, pattern, category, "block", "input", rid_suffix))

    return rules


def build_output_keyword_rules() -> list[GuardrailRule]:
    rules: list[GuardrailRule] = []
    seen: set[str] = set()
    seen_phrases: set[str] = set()

    all_block_phrases = (
        OUTPUT_BLOCK_PHRASES
        + _mirrored_output_block_phrases()
    )

    for idx, (phrase, category) in enumerate(all_block_phrases):
        phrase_key = phrase.lower()
        if phrase_key in seen_phrases:
            continue
        seen_phrases.add(phrase_key)
        rid = f"kw_out_blk_{_slug(phrase)}_{idx}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_phrase_rule(rid, phrase, category, "block", "output"))

    for idx, (phrase, category) in enumerate(OUTPUT_WARN_PHRASES):
        rid = f"kw_out_pwarn_{_slug(phrase)}_{idx}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_phrase_rule(rid, phrase, category, "warn", "output"))

    all_block_words = OUTPUT_BLOCK_WORDS + _mirrored_output_block_words()
    for idx, (word, category) in enumerate(all_block_words):
        rid = f"kw_out_wblk_{_slug(word)}_{idx}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_word_rule(rid, word, category, "block", "output"))

    all_warn_words = OUTPUT_WARN_WORDS + _mirrored_output_warn_words()
    for idx, (word, category) in enumerate(all_warn_words):
        rid = f"kw_out_wwarn_{_slug(word)}_{idx}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_word_rule(rid, word, category, "warn", "output"))

    all_block_regex = OUTPUT_BLOCK_REGEX + _mirrored_output_block_regex()
    for rid_suffix, pattern, category in all_block_regex:
        rid = f"kw_out_rx_{rid_suffix}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_regex_rule(rid, pattern, category, "block", "output", rid_suffix))

    for rid_suffix, pattern, category in OUTPUT_WARN_REGEX:
        rid = f"kw_out_rxw_{rid_suffix}"
        if rid in seen:
            continue
        seen.add(rid)
        rules.append(_regex_rule(rid, pattern, category, "warn", "output", rid_suffix))

    return rules