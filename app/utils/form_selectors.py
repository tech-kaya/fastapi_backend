from typing import List, Dict


COMMON_FORM_SELECTORS = [
    'form[id*="contact"]',
    'form[class*="contact"]',
    'form[action*="contact"]',
    '.contact-form',
    '#contact-form',
    'form',
]

FIELD_SELECTORS = {
    'name': [
        'input[name*="name"]',
        'input[id*="name"]',
        'input[placeholder*="name"]',
        'input[type="text"]:first-of-type',
        'textarea[name*="name"]',
    ],
    'email': [
        'input[name*="email"]',
        'input[id*="email"]',
        'input[type="email"]',
        'input[placeholder*="email"]',
    ],
    'phone': [
        'input[name*="phone"]',
        'input[id*="phone"]',
        'input[type="tel"]',
        'input[placeholder*="phone"]',
    ],
    'message': [
        'textarea[name*="message"]',
        'textarea[id*="message"]',
        'textarea[placeholder*="message"]',
        'textarea',
        'input[name*="message"]',
    ],
}

SUBMIT_SELECTORS = [
    'input[type="submit"]',
    'button[type="submit"]',
    'button:contains("Send")',
    'button:contains("Submit")',
    'input[value*="Send"]',
    'input[value*="Submit"]',
    '.submit-btn',
    '#submit',
]

CAPTCHA_SELECTORS = {
    'captcha_containers': [
        '.g-recaptcha',
        '.h-captcha', 
        '#captcha',
        '.captcha',
        '.recaptcha',
        '[data-sitekey]',
        '.captcha-container',
        '.verification',
        'iframe[src*="recaptcha"]',
        'iframe[src*="hcaptcha"]',
        'iframe[title*="recaptcha challenge"]',
    ],
    'captcha_checkboxes': [
        'input[type="checkbox"]#recaptcha-anchor',
        '.recaptcha-checkbox',
        '.recaptcha-checkbox-checkmark',
        'span[role="checkbox"]',
        '[aria-label*="not a robot"]',
        '.recaptcha-checkbox-border',
    ],
    'captcha_skip_buttons': [
        'button:contains("Skip")',
        'button:contains("SKIP")',
        'a:contains("Skip")',
        '.skip-btn',
        '#skip',
        '[data-action="skip"]',
        'button[onclick*="skip"]',
        '.rc-button-default:contains("Skip")',
    ],
    'captcha_images': [
        '.captcha-image',
        '.recaptcha-image-button',
        'img[src*="captcha"]',
        '.captcha-challenge img',
        '.image-select-task',
        '.rc-imageselect-payload img',
    ],
    'captcha_audio': [
        '.recaptcha-audio-button',
        'button[title*="audio"]',
        '#audio-challenge',
        '.audio-challenge',
        '.rc-button-audio',
    ],
    'recaptcha_tiles': [
        'td.rc-imageselect-tile:nth-child(1)',
        'td.rc-imageselect-tile:nth-child(2)', 
        'td.rc-imageselect-tile:nth-child(3)',
        'tr:nth-child(2) > td.rc-imageselect-tile:nth-child(1)',
        'tr:nth-child(2) > td.rc-imageselect-tile:nth-child(2)',
        'tr:nth-child(2) > td.rc-imageselect-tile:nth-child(3)',
        'tr:nth-child(3) > td.rc-imageselect-tile:nth-child(1)',
        'tr:nth-child(3) > td.rc-imageselect-tile:nth-child(2)',
        'tr:nth-child(3) > td.rc-imageselect-tile:nth-child(3)',
    ],
    'recaptcha_buttons': [
        '#recaptcha-verify-button',
        'button[id="recaptcha-verify-button"]',
        '.rc-button-default',
        'button:contains("Verify")',
        'button:contains("VERIFY")',
        'input[type="button"][value="Verify"]',
    ],
    'recaptcha_reload': [
        '#recaptcha-reload-button',
        '.rc-button-reload',
        'button[title*="Get a new challenge"]',
        'button[aria-label*="Get a new challenge"]',
    ],
}

ANTI_BOT_ELEMENTS = [
    '.cloudflare-browser-verification',
    '#challenge-form',
    '.challenge-container',
    '.bot-detection',
    '.security-check',
    'div:contains("Please wait")',
    'div:contains("Checking your browser")',
    'div:contains("Just a moment")',
    '.rc-doscaptcha-header',
    '.rc-anchor-error-msg',
    '.rc-anchor-pt',
]

RECAPTCHA_SPECIFIC_SELECTORS = {
    'iframe_challenge': [
        'iframe[title="recaptcha challenge expires in two minutes"]',
        'iframe[src*="bframe"]',
        'iframe[name*="c-"]',
    ],
    'image_grid_container': [
        '.rc-imageselect-payload',
        '.rc-imageselect-challenge',
        'table.rc-imageselect-table-33',
        'table.rc-imageselect-table-44',
    ],
    'tile_individual': {
        'row1_col1': 'tbody > tr:nth-child(1) > td:nth-child(1).rc-imageselect-tile',
        'row1_col2': 'tbody > tr:nth-child(1) > td:nth-child(2).rc-imageselect-tile',
        'row1_col3': 'tbody > tr:nth-child(1) > td:nth-child(3).rc-imageselect-tile',
        'row2_col1': 'tbody > tr:nth-child(2) > td:nth-child(1).rc-imageselect-tile',
        'row2_col2': 'tbody > tr:nth-child(2) > td:nth-child(2).rc-imageselect-tile',
        'row2_col3': 'tbody > tr:nth-child(2) > td:nth-child(3).rc-imageselect-tile',
        'row3_col1': 'tbody > tr:nth-child(3) > td:nth-child(1).rc-imageselect-tile',
        'row3_col2': 'tbody > tr:nth-child(3) > td:nth-child(2).rc-imageselect-tile',
        'row3_col3': 'tbody > tr:nth-child(3) > td:nth-child(3).rc-imageselect-tile',
    },
    'challenge_text': [
        '.rc-imageselect-desc-no-canonical',
        '.rc-imageselect-desc',
        '.rc-imageselect-desc-wrapper',
        '.rc-imageselect-instructions',
        '.rc-imageselect-challenge',
        'strong',
        '.rc-imageselect-desc strong',
        '.rc-imageselect-taskimage-wrapper strong',
    ],
    'error_indicators': [
        '.rc-imageselect-error-select-more',
        '.rc-imageselect-error-dynamic-more',
        '.rc-imageselect-incorrect-response',
    ],
}

NAVIGATION_SELECTORS = [
    'a[href*="contact"]',
    'a:contains("Contact")',
    'a:contains("Contact Us")',
    'a[title*="Contact"]',
    '.contact-link',
    '#contact-link',
]


def get_form_selector() -> str:
    return ', '.join(COMMON_FORM_SELECTORS)


def get_field_selectors(field_type: str) -> List[str]:
    return FIELD_SELECTORS.get(field_type, [])


def get_submit_selector() -> str:
    return ', '.join(SUBMIT_SELECTORS)


def get_navigation_selector() -> str:
    return ', '.join(NAVIGATION_SELECTORS)


def get_captcha_selectors(captcha_type: str) -> List[str]:
    """Get selectors for different types of CAPTCHA elements"""
    return CAPTCHA_SELECTORS.get(captcha_type, [])


def get_anti_bot_selectors() -> List[str]:
    """Get selectors for anti-bot detection elements"""
    return ANTI_BOT_ELEMENTS


def get_captcha_skip_selectors() -> List[str]:
    """Get selectors specifically for CAPTCHA skip buttons"""
    return CAPTCHA_SELECTORS.get('captcha_skip_buttons', [])


def get_all_captcha_selectors() -> str:
    """Get all CAPTCHA-related selectors as a single CSS selector"""
    all_selectors = []
    for selector_list in CAPTCHA_SELECTORS.values():
        all_selectors.extend(selector_list)
    return ', '.join(all_selectors)


def get_recaptcha_tile_selector(tile_number: int) -> str:
    """Get specific reCAPTCHA tile selector by number (1-9) to avoid strict mode violations"""
    if not 1 <= tile_number <= 9:
        raise ValueError("Tile number must be between 1 and 9")
    
    tile_selectors = CAPTCHA_SELECTORS['recaptcha_tiles']
    return tile_selectors[tile_number - 1]


def get_recaptcha_grid_selectors() -> List[str]:
    """Get all reCAPTCHA tile selectors as individual selectors"""
    return CAPTCHA_SELECTORS['recaptcha_tiles']


def get_recaptcha_verify_selectors() -> List[str]:
    """Get reCAPTCHA verify button selectors"""
    return CAPTCHA_SELECTORS['recaptcha_buttons']


def get_recaptcha_reload_selectors() -> List[str]:
    """Get reCAPTCHA reload/refresh button selectors"""
    return CAPTCHA_SELECTORS['recaptcha_reload']


def get_optimized_captcha_strategy() -> Dict[str, List[str]]:
    """Get optimized CAPTCHA handling strategy with priority order"""
    return {
        'priority_1_skip': CAPTCHA_SELECTORS['captcha_skip_buttons'],
        'priority_2_checkbox': CAPTCHA_SELECTORS['captcha_checkboxes'], 
        'priority_3_individual_tiles': CAPTCHA_SELECTORS['recaptcha_tiles'],
        'priority_4_audio': CAPTCHA_SELECTORS['captcha_audio'],
        'priority_5_reload': CAPTCHA_SELECTORS['recaptcha_reload'],
        'emergency_verify': CAPTCHA_SELECTORS['recaptcha_buttons'],
    }


def get_iframe_safe_selectors() -> List[str]:
    """Get iframe-safe selectors for nested CAPTCHA content"""
    return [
        'iframe[src*="recaptcha"] >> .rc-imageselect-tile',
        'iframe[title*="recaptcha challenge"] >> td.rc-imageselect-tile',
        '.g-recaptcha iframe >> .rc-button-default',
        'iframe[name*="c-"] >> .rc-imageselect-tile',
    ]


def get_recaptcha_iframe_selectors() -> List[str]:
    """Get reCAPTCHA iframe selectors"""
    return RECAPTCHA_SPECIFIC_SELECTORS['iframe_challenge']


def get_recaptcha_grid_container_selectors() -> List[str]:
    """Get reCAPTCHA image grid container selectors"""
    return RECAPTCHA_SPECIFIC_SELECTORS['image_grid_container']


def get_recaptcha_tile_by_position(row: int, col: int) -> str:
    """Get specific reCAPTCHA tile by row and column (1-3, 1-3)"""
    if not (1 <= row <= 3 and 1 <= col <= 3):
        raise ValueError("Row and column must be between 1 and 3")
    
    position_key = f'row{row}_col{col}'
    tiles = RECAPTCHA_SPECIFIC_SELECTORS['tile_individual']
    return tiles[position_key]


def get_recaptcha_challenge_text_selectors() -> List[str]:
    """Get reCAPTCHA challenge text/instruction selectors"""
    return RECAPTCHA_SPECIFIC_SELECTORS['challenge_text']


def get_recaptcha_error_selectors() -> List[str]:
    """Get reCAPTCHA error indicator selectors"""
    return RECAPTCHA_SPECIFIC_SELECTORS['error_indicators']


def get_anti_strict_mode_selectors() -> Dict[str, str]:
    """Get anti-strict mode selectors for reCAPTCHA tiles using unique positioning"""
    return RECAPTCHA_SPECIFIC_SELECTORS['tile_individual']


def get_comprehensive_captcha_detection() -> Dict[str, List[str]]:
    """Get comprehensive CAPTCHA detection with all types"""
    return {
        'containers': CAPTCHA_SELECTORS['captcha_containers'],
        'checkboxes': CAPTCHA_SELECTORS['captcha_checkboxes'],
        'skip_buttons': CAPTCHA_SELECTORS['captcha_skip_buttons'],
        'iframe_challenges': RECAPTCHA_SPECIFIC_SELECTORS['iframe_challenge'],
        'grid_containers': RECAPTCHA_SPECIFIC_SELECTORS['image_grid_container'],
        'error_indicators': RECAPTCHA_SPECIFIC_SELECTORS['error_indicators'],
        'anti_bot_elements': ANTI_BOT_ELEMENTS,
    }


def get_captcha_instruction_selectors() -> List[str]:
    """Get selectors for CAPTCHA instruction text (e.g., 'Select all squares with cars')"""
    return RECAPTCHA_SPECIFIC_SELECTORS['challenge_text']


def get_individual_tile_selectors() -> List[str]:
    """Get individual tile selectors to prevent strict mode violations"""
    return [
        'tbody > tr:nth-child(1) > td:nth-child(1).rc-imageselect-tile',
        'tbody > tr:nth-child(1) > td:nth-child(2).rc-imageselect-tile',
        'tbody > tr:nth-child(1) > td:nth-child(3).rc-imageselect-tile',
        'tbody > tr:nth-child(2) > td:nth-child(1).rc-imageselect-tile',
        'tbody > tr:nth-child(2) > td:nth-child(2).rc-imageselect-tile',
        'tbody > tr:nth-child(2) > td:nth-child(3).rc-imageselect-tile',
        'tbody > tr:nth-child(3) > td:nth-child(1).rc-imageselect-tile',
        'tbody > tr:nth-child(3) > td:nth-child(2).rc-imageselect-tile',
        'tbody > tr:nth-child(3) > td:nth-child(3).rc-imageselect-tile',
    ]


def get_safe_tile_selector(tile_position: int) -> str:
    """
    Get safe tile selector for specific position (1-9) to avoid strict mode violations
    
    Args:
        tile_position: Position of tile (1-9), where 1 is top-left, 9 is bottom-right
        
    Returns:
        CSS selector for specific tile
    """
    if not 1 <= tile_position <= 9:
        raise ValueError("Tile position must be between 1 and 9")
    
    # Map position to row/column
    row = ((tile_position - 1) // 3) + 1
    col = ((tile_position - 1) % 3) + 1
    
    return f'tbody > tr:nth-child({row}) > td:nth-child({col}).rc-imageselect-tile'


def get_captcha_strategy_selectors() -> Dict[str, List[str]]:
    """Get comprehensive CAPTCHA strategy with priority-based selectors"""
    return {
        'instruction_text': RECAPTCHA_SPECIFIC_SELECTORS['challenge_text'],
        'skip_buttons': CAPTCHA_SELECTORS['captcha_skip_buttons'],
        'checkbox': CAPTCHA_SELECTORS['captcha_checkboxes'],
        'individual_tiles': get_individual_tile_selectors(),
        'verify_buttons': CAPTCHA_SELECTORS['recaptcha_buttons'],
        'audio_buttons': CAPTCHA_SELECTORS['captcha_audio'],
        'reload_buttons': CAPTCHA_SELECTORS['recaptcha_reload'],
        'error_indicators': RECAPTCHA_SPECIFIC_SELECTORS['error_indicators'],
    }


def get_captcha_abandonment_selectors() -> Dict[str, List[str]]:
    """Get selectors for CAPTCHA abandonment detection"""
    return {
        'strict_mode_errors': [
            'div:contains("strict mode violation")',
            'error:contains("strict mode")',
            '.error-message:contains("strict mode")',
        ],
        'timeout_indicators': [
            'div:contains("timeout")',
            'div:contains("expired")',
            '.timeout-message',
        ],
        'blocking_indicators': [
            'div:contains("blocked")',
            'div:contains("access denied")',
            '.access-denied',
        ],
    } 