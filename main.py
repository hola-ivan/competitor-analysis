import requests
import json
import toml
import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Competitive Analysis Tool",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton button {
        width: 100%;
        border-radius: 5px;
    }
    .example-container {
        padding: 1rem;
        border-radius: 5px;
        background-color: #f0f2f6;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header section
st.title("🎯 Competitive Intelligence Assistant")
st.markdown("""
    ### WHU GenAI Builder's Club - Challenge 2
    
    This tool helps you:
    - 📊 Identify your most relevant competitors
    - 💰 Track competitor funding and market position
    - ⚡ Get actionable insights for differentiation
    
    Simply describe your company below or try one of our examples to get started.
    
    Contact me at: ai@holaivan.tech
""")

# Load secrets and setup API
secrets = toml.load('.streamlit/secrets.toml')
auth_token = secrets['api']['dify_token']

url = "https://api.dify.ai/v1/chat-messages"
headers = {
    'Authorization': f'Bearer {auth_token}',
    'Content-Type': 'application/json',
}

# Example companies in a more structured format
example_companies = {
    "Tech Startup": {
        "description": "We are a B2B SaaS startup based in Berlin, developing AI-powered customer service automation software. Our solution reduces response times by 80% and costs by 60%. We target medium to large enterprises in Europe, offering subscription plans starting at €999/month with custom enterprise pricing.",
        "icon": "💻"
    },
    "Local Restaurant": {
        "description": "We're an upscale Mexican restaurant in Bonn, specializing in authentic Northern Mexican cuisine with farm-to-table ingredients. Our target customers are urban professionals and food enthusiasts aged 25-45. We offer a rotating seasonal menu with entrees $28-45, emphasizing organic and locally-sourced ingredients.",
        "icon": "🌮"
    },
    "Jewelry Company": {
        "description": "Based in Portland, we create handcrafted jewelry using 100% recycled precious metals and ethically sourced gemstones. We target environmentally conscious consumers aged 25-40 through our direct-to-consumer e-commerce platform. Our pieces range from $200-2000, with a subscription box option at $99/month.",
        "icon": "💎"
    }
}

# Create columns for example buttons
st.subheader("📌 Quick Start Examples")
cols = st.columns(len(example_companies))
for col, (company, info) in zip(cols, example_companies.items()):
    with col:
        st.markdown(f"<div class='example-container'>", unsafe_allow_html=True)
        if st.button(f"{info['icon']} {company}"):
            st.session_state['company_description'] = info['description']
        st.markdown("</div>", unsafe_allow_html=True)

# Main input section
st.subheader("🏢 Company Analysis")
company_description = st.text_area(
    "Describe your company, products, and target market:",
    height=150,
    placeholder="Example: We are a sustainable fashion brand focusing on eco-friendly materials and ethical manufacturing...",
    value=st.session_state.get('company_description', '')
)

# Analysis section
if st.button("🔍 Analyze Competition", type="primary"):
    if company_description:
        with st.spinner("Analyzing your competitive landscape..."):
            data = {
                "inputs": {"company_description": company_description},
                "query": "begin",
                "response_mode": "streaming",
                "user": "abc-123"
            }
            
            try:
                response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
                
                if response.status_code == 200:
                    # Create placeholder for content
                    content_placeholder = st.empty()
                    accumulated_content = ""
                    
                    # Process streaming response
                    for line in response.iter_lines():
                        if line:
                            line = line.decode('utf-8')
                            if line.startswith("data: "):
                                try:
                                    json_str = line[6:]  # Remove "data: " prefix
                                    event_data = json.loads(json_str)
                                    
                                    if "answer" in event_data:
                                        accumulated_content += event_data["answer"]
                                        content_placeholder.markdown(accumulated_content)
                                    elif "thought" in event_data:
                                        thought_content = event_data["thought"]
                                        st.markdown(thought_content)
                                        
                                except json.JSONDecodeError:
                                    continue
                    
                    # Parse accumulated content into sections
                    if accumulated_content:
                        sections = accumulated_content.split("##")
                        competitors_section = next((s for s in sections if "Key Competitors" in s), "")
                        funding_section = next((s for s in sections if "Funding Analysis" in s), "")
                        insights_section = next((s for s in sections if "Strategic Insights" in s), "")

                        # Display results in tabs
                        tab1, tab2, tab3 = st.tabs(["🎯 Key Competitors", "💰 Funding Analysis", "⚡ Strategic Insights"])
                        
                        with tab1:
                            st.markdown("### Key Competitors")
                            st.markdown(competitors_section)
                        
                        with tab2:
                            st.markdown("### Funding Analysis") 
                            st.markdown(funding_section)
                            
                        with tab3:
                            st.markdown("### Strategic Insights")
                            st.markdown(insights_section)
                
                else:
                    st.error(f"API request failed with status code: {response.status_code}")
                    st.code(response.text)

            except requests.RequestException as e:
                st.error("Failed to connect to the API")
                st.exception(e)
            except Exception as e:
                st.error("An unexpected error occurred")
                st.exception(e)
    else:
        st.warning("⚠️ Please enter a company description to begin the analysis.")

# Footer
st.markdown("---")
st.markdown("### 💡 Tips for best results")
st.markdown("""
- Be specific about your product/service offerings
- Include your target market and geographic location
- Mention any unique selling propositions
- Describe your business model and pricing strategy
""")