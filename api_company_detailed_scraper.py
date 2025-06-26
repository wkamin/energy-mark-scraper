from dotenv import load_dotenv
import os
import requests
import csv
import time
import sys

load_dotenv()

API_URL = os.getenv("API_URL")
DETAIL_URL_TEMPLATE = os.getenv("DETAIL_URL_TEMPLATE")
AUTH_TOKEN = os.getenv("AUTH_TOKEN")
RESULTS_PER_PAGE = 100

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def fetch_page(page_number):
    payload = {
        "operationName": "companyProfiles",
        "variables": {
            "topicTags": [],
            "currentPageNumber": page_number,
            "resultsPerPage": RESULTS_PER_PAGE,
            "sortByColumnName": "storefront_updated_at",
            "sortOrder": "desc",
            "isDarcyPresenter": False,
            "strategicPartner": None,
            "technologyState": None,
            "fundingRounds": None,
            "amountsRaised": [],
            "keyword": "",
            "serviceLineIds": []
        },
        "query": """query companyProfiles($currentPageNumber: Int, $resultsPerPage: Int, $sortByColumnName: String, $sortOrder: String, $topicTags: [String!], $filterBy: String, $isStorefrontPublished: Boolean, $isDarcyPresenter: Boolean, $topInnovatorYearRange: String, $strategicPartner: String, $technologyState: String, $fundingRounds: String, $amountsRaised: [String!], $keyword: String, $serviceLineIds: [ID!]) { companyProfiles(currentPageNumber: $currentPageNumber resultsPerPage: $resultsPerPage sortByColumnName: $sortByColumnName sortOrder: $sortOrder topicTags: $topicTags filterBy: $filterBy isStorefrontPublished: $isStorefrontPublished isDarcyPresenter: $isDarcyPresenter topInnovatorYearRange: $topInnovatorYearRange strategicPartner: $strategicPartner technologyState: $technologyState fundingRounds: $fundingRounds amountsRaised: $amountsRaised keyword: $keyword serviceLineIds: $serviceLineIds ) { company { id name logoUrl slug __typename } serviceLines { name __typename } topicTags { name category __typename } id description headquartersCountry employees totalFundingAmount isVendorMaterialsShown lastFeaturedDarcyLiveEventUrl lastFeaturedInDarcyLiveAt isAccessible __typename } }"""
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    data = response.json()
    return data["data"]["companyProfiles"]

def fetch_company_detail(slug):
    url = DETAIL_URL_TEMPLATE.format(slug)
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def extract_topic_tags(included):
    tags = []
    for item in included:
        if item.get("type") == "topic_tag":
            tag_name = item.get("attributes", {}).get("name")
            if tag_name:
                tags.append(tag_name)
    return ", ".join(tags)

def flatten_company_detail(detail):
    attrs = detail.get("data", {}).get("attributes", {})
    flat = {
        "name": attrs.get("name"),
        "slug": attrs.get("slug"),
        "tagline": attrs.get("tagline"),
        "description": attrs.get("description"),
        "short_description": attrs.get("short_description"),
        "founded": attrs.get("founded"),
        "headquarters": attrs.get("headquarters"),
        "headquarters_country": attrs.get("headquarters_country"),
        "headquarters_state": attrs.get("headquarters_state"),
        "employees": attrs.get("employees"),
        "tech_stage": attrs.get("tech_stage"),
        "markets": attrs.get("markets"),
        "logo_url": attrs.get("logo_url"),
        "canonical_url": attrs.get("canonical_url"),
        "company_type": attrs.get("company_type"),
        "is_published": attrs.get("is_published"),
        "is_darcy_presenter": attrs.get("is_darcy_presenter"),
        "is_darcy_insights_shown": attrs.get("is_darcy_insights_shown"),
        "is_vendor_overview_shown": attrs.get("is_vendor_overview_shown"),
        "is_vendor_materials_shown": attrs.get("is_vendor_materials_shown"),
        "is_accessible": attrs.get("is_accessible"),
        "views_count": attrs.get("views_count"),
        "shares_count": attrs.get("shares_count"),
        "likes_count": attrs.get("likes_count"),
        "follows_count": attrs.get("follows_count"),
        "company_id": attrs.get("company_id"),
        "updated_at": attrs.get("updated_at"),
        "storefront_updated_at": attrs.get("storefront_updated_at"),
        "storefront_published_at": attrs.get("storefront_published_at"),
        "full_storefront_completed_at": attrs.get("full_storefront_completed_at"),
        "meta_title": attrs.get("meta_title"),
        "meta_description": attrs.get("meta_description"),
        "product_overview_safe_html": attrs.get("product_overview_safe_html"),
        "business_model_safe_html": attrs.get("business_model_safe_html"),
        "technology_innovations_safe_html": attrs.get("technology_innovations_safe_html"),
        "applications_description_safe_html": attrs.get("applications_description_safe_html"),
        "reactions_count": attrs.get("reactions_count"),
        "company_accessible_views_count": attrs.get("company_accessible_views_count"),
        "top_innovator_years": ", ".join(attrs.get("top_innovator_years", [])),
        "is_assigned_to_current_user": attrs.get("is_assigned_to_current_user"),
        "is_managed_by_current_user": attrs.get("is_managed_by_current_user"),
        "is_shared_by_current_user": attrs.get("is_shared_by_current_user"),
        "is_followed_by_current_user": attrs.get("is_followed_by_current_user"),
    }
    return flat

def print_progress(current, total):
    percent = (current / total) * 100
    bar_length = 40
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {current}/{total} ({percent:.1f}%)')
    sys.stdout.flush()
    if current == total:
        print()

def main():
    print("Fetching company list...")
    companies = []
    page = 1
    while True:
        page_data = fetch_page(page)
        if not page_data:
            break
        companies.extend(page_data)
        if len(page_data) < RESULTS_PER_PAGE:
            break
        page += 1
    print(f"Found {len(companies)} companies. Fetching details...")

    all_rows = []
    total = len(companies)
    for idx, company in enumerate(companies):
        slug = company["company"]["slug"]
        try:
            detail = fetch_company_detail(slug)
            flat = flatten_company_detail(detail)
            topic_tags = extract_topic_tags(detail.get("included", []))
            flat["topic_tags"] = topic_tags
            all_rows.append(flat)
            if idx == 0:
                print("Sample detail fields:")
                print(flat)
        except Exception as e:
            print(f"\nError fetching details for {slug}: {e}")
        print_progress(idx + 1, total)
        time.sleep(0.2)  # Be nice to the API

    # Write to CSV
    if all_rows:
        fieldnames = list(all_rows[0].keys())
        with open("company_profiles_detailed.csv", "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_rows)
    print("Done. Data written to company_profiles_detailed.csv")

if __name__ == "__main__":
    main() 