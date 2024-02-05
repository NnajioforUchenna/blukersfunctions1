from services.dbServices.firebase_services import db


def searchJobPostsByParameter(nameRelated, locationRelated):
    # Convert parameters to lowercase and check if they're empty
    nameRelated = nameRelated.strip().lower() if nameRelated else None
    locationRelated = locationRelated.strip().lower() if locationRelated else None

    # If both parameters are empty, return an empty list
    if nameRelated is None and locationRelated is None:
        return []

    jobposts_ref = db.collection('JobPosts')
    query_ref = jobposts_ref.stream()

    matched_jobposts = []

    for jobpost_doc in query_ref:
        jobpost_data = jobpost_doc.to_dict()

        if 'jobPostId' in jobpost_data:
            print(jobpost_data['jobPostId'])

        # Check name-related fields including company name, job title, requirements, skills, industry IDs, and job IDs
        if nameRelated:
            name_matched = False
            for field in ['companyName', 'jobTitle', 'requirements']:
                if field in jobpost_data and nameRelated in str(jobpost_data[field]).strip().lower():
                    matched_jobposts.append(jobpost_data)
                    name_matched = True
                    break
            if not name_matched:
                for field in ['industryIds', 'jobIds', 'skills']:
                    if field in jobpost_data and any(
                            nameRelated in str(item).strip().lower() for item in jobpost_data[field]):
                        matched_jobposts.append(jobpost_data)
                        break

        # Check location-related fields in all addresses, including 'address'
        if locationRelated:
            location_matched = False
            if 'addresses' in jobpost_data and jobpost_data['addresses'] is not None:
                for address in jobpost_data['addresses']:
                    if address is None:
                        continue
                    for field in ['city', 'state', 'country']:
                        if field in address:
                            value = address[field]
                            if value is not None and locationRelated in str(value).strip().lower():
                                matched_jobposts.append(jobpost_data)
                                location_matched = True
                                break
                        if location_matched:
                            break
            if not location_matched and 'address' in jobpost_data and jobpost_data['address'] is not None:
                for field in ['city', 'state', 'country']:
                    if field in jobpost_data['address']:
                        value = jobpost_data['address'][field]
                        if value is not None and locationRelated in str(value).strip().lower():
                            matched_jobposts.append(jobpost_data)
                            break

    return matched_jobposts
