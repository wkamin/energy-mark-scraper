import requests
import csv

API_URL = "https://api.darcypartners.com/graphql"
AUTH_TOKEN = "ec050afb8acf39def17e11c51e51f969"  # Replace with your actual token
RESULTS_PER_PAGE = 100  # Increase for fewer requests if allowed

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
        "query": """query companyProfiles($currentPageNumber: Int, $resultsPerPage: Int, $sortByColumnName: String, $sortOrder: String, $topicTags: [String!], $filterBy: String, $isStorefrontPublished: Boolean, $isDarcyPresenter: Boolean, $topInnovatorYearRange: String, $strategicPartner: String, $technologyState: String, $fundingRounds: String, $amountsRaised: [String!], $keyword: String, $serviceLineIds: [ID!]) {\n  companyProfiles(\n    currentPageNumber: $currentPageNumber\n    resultsPerPage: $resultsPerPage\n    sortByColumnName: $sortByColumnName\n    sortOrder: $sortOrder\n    topicTags: $topicTags\n    filterBy: $filterBy\n    isStorefrontPublished: $isStorefrontPublished\n    isDarcyPresenter: $isDarcyPresenter\n    topInnovatorYearRange: $topInnovatorYearRange\n    strategicPartner: $strategicPartner\n    technologyState: $technologyState\n    fundingRounds: $fundingRounds\n    amountsRaised: $amountsRaised\n    keyword: $keyword\n    serviceLineIds: $serviceLineIds\n  ) {\n    company {\n      id\n      name\n      logoUrl\n      slug\n    }\n    serviceLines {\n      name\n    }\n    topicTags {\n      name\n      category\n    }\n    id\n    description\n    headquartersCountry\n    employees\n    totalFundingAmount\n    isVendorMaterialsShown\n    lastFeaturedDarcyLiveEventUrl\n    lastFeaturedInDarcyLiveAt\n    isAccessible\n  }\n}"""
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["data"]["companyProfiles"]

# Fetch all pages
all_data = []
page = 1
while True:
    print(f"Fetching page {page}...")
    page_data = fetch_page(page)
    if not page_data:
        break
    all_data.extend(page_data)
    if len(page_data) < RESULTS_PER_PAGE:
        break
    page += 1

# Write to CSV
with open("company_profiles.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Company Name", "Description", "Link", "Logo URL", "Service Lines", "Topic Tags", "Headquarters Country", "Employees", "Total Funding", "Is Vendor Materials Shown", "Featured Event URL", "Featured In Darcy Live At", "Is Accessible", "Company ID", "Profile ID"
    ])
    for item in all_data:
        company = item["company"]
        name = company.get("name", "")
        description = item.get("description", "")
        link = f"https://darcypartners.com/innovators/{company.get('slug', '')}"
        logo_url = company.get("logoUrl", "")
        service_lines = ", ".join([sl["name"] for sl in item.get("serviceLines", [])])
        topic_tags = ", ".join([tt["name"] for tt in item.get("topicTags", [])])
        headquarters = item.get("headquartersCountry", "")
        employees = item.get("employees", "")
        funding = item.get("totalFundingAmount", "")
        is_vendor_materials_shown = item.get("isVendorMaterialsShown", "")
        featured_event_url = item.get("lastFeaturedDarcyLiveEventUrl", "")
        featured_in_darcy = item.get("lastFeaturedInDarcyLiveAt", "")
        is_accessible = item.get("isAccessible", "")
        company_id = company.get("id", "")
        profile_id = item.get("id", "")
        writer.writerow([
            name, description, link, logo_url, service_lines, topic_tags, headquarters, employees, funding, is_vendor_materials_shown, featured_event_url, featured_in_darcy, is_accessible, company_id, profile_id
        ])

print("Saved to company_profiles.csv") 