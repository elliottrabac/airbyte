import os
from algoliasearch.search_client import SearchClient, SearchConfig
import urllib
import time

from airbyte_cdk.logger import AirbyteLogger


def scrapper_job_offers(logger: AirbyteLogger, urls):

    results = []
    for url_id, url in enumerate(urls):
        url = url.split("?")[-1]
        logger.info(f"Search: {url}")
        dummy = urllib.parse.unquote(url)

        dummy = dummy.split("&")
        query = ""
        aroundRadius = ""
        aroundLatLng = ""
        experience_level_minimum = 0
        experience_level_maximum = 15
        params = []
        facetFilters = []
        for each in dummy:
            if "page=" in each or "aroundQuery" in each:
                pass
            elif ("refinementList[") in each:
                each = each.replace("refinementList[", "")
                each = each.replace("[]=", ":")
                each = each.replace("]", "")
                facetFilters.append(each)
            elif ("aroundRadius") in each:
                aroundRadius = each.replace("aroundRadius=", "")
            elif ("aroundLatLng") in each:
                aroundLatLng = each.replace("aroundLatLng=", "")
            elif ("query") in each:
                query = each.replace("query=", "")
            elif ("experience_level_minimum") in each and "[min]" in each:
                experience_level_minimum = each.split("=")[-1]
            elif ("experience_level_minimum") in each and "[max]" in each:
                experience_level_maximum = each.split("=")[-1]
            else:
                each = each.replace("=", "':'")
                params.append(each)

        sectors = []
        profession = []
        office = []
        organization = []
        contract_type_names = []
        language = []
        for each in facetFilters:
            if "sectors_name" in each:
                sectors.append(each)
            elif "profession_name" in each:
                profession.append(each)
            elif "office." in each:
                office.append(each)
            elif "organization." in each:
                organization.append(each)
            elif "contract_type_names." in each:
                contract_type_names.append(each)
            elif "language:" in each:
                language.append(each)

        if aroundRadius == "" and aroundLatLng == "" and len(office) == 0:
            office = ["office.country_code:FR"]

        trial = 0
        while trial < 4:
            try:
                ApplicationID = "CSEKHVMS53"
                APIKey = "02f0d440abc99cae37e126886438b266"
                indexname = "wk_cms_jobs_production"

                config = SearchConfig(ApplicationID, APIKey)
                config.headers["referer"] = "https://www.welcometothejungle.com/"
                config.headers[
                    "User-Agent"
                ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36"

                client = SearchClient.create_with_config(config)
                index = client.init_index(indexname)

                aa = index.browse_objects(
                    {
                        "query": query,
                        "attributesToRetrieve": [
                            "slug",
                            "name",
                            "organization",
                            "contract_type",
                            "office",
                            "published_at",
                            "profession",
                        ],
                        "filters": "website.reference:wttj_fr",
                        "disableTypoToleranceOnAttributes": ["profile"],
                        "aroundLatLng": aroundLatLng,
                        "aroundRadius": aroundRadius,
                        "aroundPrecision": aroundRadius,
                        "maxValuesPerFacet": 100,
                        "numericFilters": [
                            "experience_level_minimum>=%s" % str(experience_level_minimum),
                            "experience_level_minimum<=%s" % str(experience_level_maximum),
                        ],
                        "facetFilters": [office, sectors, profession, contract_type_names, organization, language],
                    }
                )

                hits = []
                for hit in aa:
                    hits.append(hit)

                res = []
                for each in hits:
                    try:
                        title = each["name"]
                        contract = each["contract_type"]
                        location = each["office"]["city"]
                        company = each["organization"]["name"]
                        company_slug = each["organization"]["slug"]
                        date = each["published_at"]
                        category = each["profession"]["category"]["fr"]
                        profession = each["profession"]["name"]["fr"]
                        com_website = (
                            "https://www.welcometothejungle.com/fr/companies/%s"
                            % each["organization"]["website_organization"]["slug"]
                        )
                        job_post = "%s/jobs/%s" % (com_website, each["slug"])
                        search_url = "https://www.welcometothejungle.com/fr/jobs?%s" % url
                        slug = each["slug"]
                        res.append(
                            {
                                "JOB_TITLE": title,
                                "PUBLISHED_AT": date,
                                "CONTRACT_TYPE": contract,
                                "LOCATION": location,
                                "COMPANY_NAME": company,
                                "COMPANY_SLUG": company_slug,
                                "CATEGORY": category,
                                "SUB_CATEGORY": profession,
                                "COMPANY_URL": com_website,
                                "URL": job_post,
                                "SLUG": slug,
                            }
                        )
                    except:
                        pass

                results += res
                trial = 100
            except Exception as e:
                logger.info("Failed to fetch data from the website. ")
                logger.info(e)
                if trial == 3:
                    logger.info("Please verify search URL and try again later.")
                else:
                    logger.info("Retrying..")
                time.sleep(2)
            trial = trial + 1

    logger.info("Total results found: %s" % str(len(results)))

    return results
