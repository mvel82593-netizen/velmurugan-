from __future__ import annotations

import html
import os
import re

import requests
import streamlit as st

from dotenv import load_dotenv


load_dotenv()


DEFAULT_BACKEND = os.getenv(
    "BACKEND_URL",
    "http://127.0.0.1:8000"
).rstrip("/")


st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide"
)


st.markdown(
    """
    <style>

    .main-title {
        text-align: center;
        font-size: 2.4rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        text-align: center;
        color: #9aa4b2;
        margin-bottom: 1.5rem;
    }

    .legal-card {

        background: #101722;

        border: 1px solid #263242;

        border-radius: 14px;

        padding: 24px;

        line-height: 1.65;

        max-height: 650px;

        overflow-y: auto;

        color: #e8edf3;
    }

    .notice {

        background: #2b2110;

        border: 1px solid #6c5118;

        border-radius: 10px;

        padding: 12px 14px;

        color: #f4df9b;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.markdown(
    '<div class="main-title">⚖️ LegalEase</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="sub-title">'
    'AI-Powered Legal Document Generator'
    '</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="notice">'
    'Drafting assistance only — review generated '
    'legal content with a qualified legal professional '
    'before signing or relying on it.'
    '</div>',
    unsafe_allow_html=True
)


if "document" not in st.session_state:

    st.session_state.document = ""


if "generated_type" not in st.session_state:

    st.session_state.generated_type = ""


with st.sidebar:

    st.header("⚙️ Settings")

    backend = st.text_input(
        "FastAPI Backend URL",
        DEFAULT_BACKEND
    )

    st.caption(
        "FastAPI must be running before generation."
    )

    st.divider()

    st.markdown("### Document examples")

    st.write("• Employment Contract")
    st.write("• NDA")
    st.write("• Lease Agreement")
    st.write("• Freelance Contract")
    st.write("• Offer Letter")


left, right = st.columns(
    [0.9, 1.1],
    gap="large"
)


with left:

    st.subheader(
        "📝 Document Details"
    )

    document_type = st.text_input(
        "Document Type",
        placeholder=(
            "e.g. Freelance Work Contract"
        )
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=120
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Provider delivers work by deadline; "
            "Confidentiality must be maintained"
        ),
        height=180,
        help=(
            "Separate individual terms using semicolons."
        )
    )

    dates = st.text_input(
        "Effective Date",
        placeholder="e.g. April 10, 2025"
    )

    generate = st.button(
        "✨ Generate Document",
        type="primary",
        use_container_width=True
    )


    if generate:

        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "dates": dates
        }

        missing = [
            key
            for key, value in payload.items()
            if not value.strip()
        ]

        if missing:

            st.error(
                "Please complete all fields."
            )

        else:

            try:

                with st.spinner(
                    "Generating your legal draft..."
                ):

                    response = requests.post(
                        f"{backend.rstrip('/')}/api/generate",
                        json=payload,
                        timeout=120
                    )

                if response.ok:

                    data = response.json()

                    st.session_state.document = (
                        data["content"]
                    )

                    st.session_state.generated_type = (
                        data["document_type"]
                    )

                    if data.get("demo_mode"):

                        st.warning(
                            "Demo mode is active. "
                            "Connect Gemini for AI-generated content."
                        )

                    else:

                        st.success(
                            "Document generated successfully."
                        )

                else:

                    try:

                        detail = response.json().get(
                            "detail",
                            response.text
                        )

                    except Exception:

                        detail = response.text

                    st.error(
                        f"Backend error: {detail}"
                    )

            except requests.RequestException as exc:

                st.error(
                    "Could not connect to FastAPI.\n\n"
                    f"{exc}"
                )


with right:

    st.subheader(
        "📄 Document Preview"
    )

    if st.session_state.document:

        edit = st.checkbox(
            "✏️ Click to Edit Document"
        )

        if edit:

            edited = st.text_area(
                "Editable Document",
                value=st.session_state.document,
                height=600
            )

            st.session_state.document = edited

        else:

            safe = html.escape(
                st.session_state.document
            )

            safe = re.sub(
                r"(?m)^([A-Z][A-Z0-9 &,'()/.-]{3,})$",
                r"<h3>\1</h3>",
                safe
            )

            safe = safe.replace(
                "\n",
                "<br>"
            )

            st.markdown(
                f'<div class="legal-card">{safe}</div>',
                unsafe_allow_html=True
            )


        st.divider()

        st.subheader(
            "⬇️ Download"
        )

        from backend.services.document_formatter import (
            format_docx,
            format_pdf
        )


        content = (
            st.session_state.document
            .encode("utf-8")
        )


        doc_name = re.sub(
            r"[^a-zA-Z0-9_-]+",
            "_",
            st.session_state.generated_type
            or "document"
        ).strip("_").lower()


        col1, col2, col3 = st.columns(3)


        with col1:

            st.download_button(
                "⬇️ TXT",
                data=content,
                file_name=f"{doc_name}.txt",
                mime="text/plain",
                use_container_width=True
            )


        with col2:

            st.download_button(
                "⬇️ DOCX",
                data=format_docx(
                    st.session_state.document,
                    st.session_state.generated_type
                ),
                file_name=f"{doc_name}.docx",
                mime=(
                    "application/vnd.openxmlformats-officedocument."
                    "wordprocessingml.document"
                ),
                use_container_width=True
            )


        with col3:

            st.download_button(
                "⬇️ PDF",
                data=format_pdf(
                    st.session_state.document,
                    st.session_state.generated_type
                ),
                file_name=f"{doc_name}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    else:

        st.info(
            "Your generated document will appear here."
        )