import streamlit as st
import os
import base64
from openai import OpenAI

def translate_prompt(korean_prompt, api_key):
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "당신은 프롬프트를 한국어에서 영어로 번역하는 전문가입니다. 이미지 생성을 위한 프롬프트를 정확하고 자연스럽게 번역해주세요."},
                {"role": "user", "content": f"다음 이미지 생성 프롬프트를 영어로 자연스럽게 번역해주세요: '{korean_prompt}'"}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"번역 중 오류 발생: {str(e)}")
        return korean_prompt

def enhance_prompt(prompt, api_key):
    try:
        enhancement_prompt = f"""Enhance this image generation prompt to create a more detailed and effective prompt.\nOriginal prompt: \"{prompt}\"\nMake it more descriptive and specific, adding details about composition, mood, lighting, and style where appropriate.\nDo not change the core subject or main elements of the image. Do not add any explanation, just return the enhanced prompt."""
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert in writing effective image generation prompts. Your task is to enhance prompts to get better results from image generation AI."},
                {"role": "user", "content": enhancement_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"프롬프트 향상 중 오류 발생: {str(e)}")
        return prompt

def generate_image_with_gpt_image_1(prompt, api_key):
    try:
        client = OpenAI(api_key=api_key)
        result = client.images.generate(
            model="gpt-image-1",
            prompt=prompt
        )
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        return image_bytes
    except Exception as e:
        st.error(f"이미지 생성 중 오류: {str(e)}")
        return None

def main():
    st.title("🖼️ GPT Image 1 - AI 이미지 생성기 (1024x1536, Low)")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.error("OPENAI_API_KEY 환경 변수가 설정되어 있지 않습니다.")
        return

    st.header("프롬프트 입력")
    prompt_language = st.selectbox("프롬프트 언어", ["한국어 (자동 번역)", "영어 (직접 입력)"])
    prompt = ""
    if prompt_language == "한국어 (자동 번역)":
        korean_prompt = st.text_area("원하는 이미지를 한국어로 설명하세요:", height=100)
        if korean_prompt:
            with st.spinner("프롬프트를 영어로 번역 중..."):
                english_prompt = translate_prompt(korean_prompt, api_key)
                st.success("번역 완료!")
                with st.expander("영어로 번역된 프롬프트"):
                    st.write(english_prompt)
                prompt = english_prompt
    else:
        prompt = st.text_area("이미지에 대한 상세한 설명을 영어로 입력하세요:", height=100)

    if prompt:
        if st.checkbox("AI로 프롬프트 향상시키기", value=False):
            with st.spinner("프롬프트를 향상시키는 중..."):
                enhanced_prompt = enhance_prompt(prompt, api_key)
                st.success("향상 완료!")
                with st.expander("향상된 프롬프트"):
                    st.write(enhanced_prompt)
                prompt = enhanced_prompt

    if prompt and st.button("이미지 생성"):
        with st.spinner("이미지 생성 중입니다..."):
            image_bytes = generate_image_with_gpt_image_1(prompt, api_key)
            if image_bytes:
                st.image(image_bytes, caption="생성된 이미지 (1024x1536, Low)")
                st.download_button(
                    label="이미지 다운로드",
                    data=image_bytes,
                    file_name="generated_image.png",
                    mime="image/png"
                )

if __name__ == "__main__":
    main() 