from transformers import MBartForConditionalGeneration, MBart50Tokenizer, MBartConfig
import pandas as pd
import os

# load model and tokenizer
model_name = "facebook/mbart-large-50-many-to-many-mmt"
model = MBartForConditionalGeneration.from_pretrained(model_name)
tokenizer = MBart50Tokenizer.from_pretrained(model_name)

# # print language and id
# for lang, id in tokenizer.lang_code_to_id.items():
#     print(f"Language Code: {lang}, ID: {id}")

# generate language map
supported_languages = {
    'AR': 'ar_AR',
    'CS': 'cs_CZ',
    'DE': 'de_DE',
    'EN': 'en_XX',
    'ES': 'es_XX',
    'ET': 'et_EE',
    'FI': 'fi_FI',
    'FR': 'fr_XX',
    'GU': 'gu_IN',
    'HI': 'hi_IN',
    'IT': 'it_IT',
    'JA': 'ja_XX',
    'KK': 'kk_KZ',
    'KO': 'ko_KR',
    'LT': 'lt_LT',
    'LV': 'lv_LV',
    'MY': 'my_MM',
    'NE': 'ne_NP',
    'NL': 'nl_XX',
    'RO': 'ro_RO',
    'RU': 'ru_RU',
    'SI': 'si_LK',
    'TR': 'tr_TR',
    'VI': 'vi_VN',
    'ZH': 'zh_CN',
    'AF': 'af_ZA',
    'AZ': 'az_AZ',
    'BN': 'bn_IN',
    'FA': 'fa_IR',
    'HE': 'he_IL',
    'HR': 'hr_HR',
    'ID': 'id_ID',
    'KA': 'ka_GE',
    'KM': 'km_KH',
    'MK': 'mk_MK',
    'ML': 'ml_IN',
    'MN': 'mn_MN',
    'MR': 'mr_IN',
    'PL': 'pl_PL',
    'PS': 'ps_AF',
    'PT': 'pt_XX',
    'SV': 'sv_SE',
    'SW': 'sw_KE',
    'TA': 'ta_IN',
    'TE': 'te_IN',
    'TH': 'th_TH',
    'TL': 'tl_XX',
    'UK': 'uk_UA',
    'UR': 'ur_PK',
    'XH': 'xh_ZA',
    'GL': 'gl_ES',
    'SL': 'sl_SI',
}

def summarization(text, lang_code):
    # use lang map to get supported lang code
    mbart_lang_code = supported_languages.get(lang_code[:2])
    if not mbart_lang_code:
        return text
    
    # set input language
    tokenizer.src_lang = mbart_lang_code
    # encode text
    encoded = tokenizer(text, max_length=1025, truncation=True, return_tensors="pt")
    # generate summary
    summary_ids = model.generate(encoded['input_ids'], num_beams=4, max_length=256, early_stopping=True)
    # decode summary
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

base_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(base_dir)
data_dir = os.path.join(parent_dir, 'data/AGRI/')
full_path = os.path.join(data_dir, 'processed_data.csv')
df = pd.read_csv(full_path)

print(df.iloc[1])

df_test = df.iloc[1]
summary = summarization(df_test['Feedback'], df_test['language'])
print(df_test['Feedback'], '.....................',summary)