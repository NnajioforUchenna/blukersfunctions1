from services.dbServices.firebase_services import db


def searchWorkersByParameter(nameRelated, locationRelated):
    # Convert parameters to lowercase and check if they're empty
    nameRelated = nameRelated.strip().lower() if nameRelated else None
    locationRelated = locationRelated.strip().lower() if locationRelated else None

    # If both parameters are empty, return an empty list
    if nameRelated is None and locationRelated is None:
        return []

    workers_ref = db.collection('workers')
    query_ref = workers_ref.stream()

    matched_workers = []

    for worker_doc in query_ref:
        worker_data = worker_doc.to_dict()

        if 'workerId' in worker_data:
            print(worker_data['workerId'])

        # Check name-related fields including skills and jobIds
        if nameRelated:
            name_matched = False
            for field in ['firstName', 'middleName', 'lastName']:
                if field in worker_data and nameRelated in str(worker_data[field]).strip().lower():
                    matched_workers.append(worker_data)
                    name_matched = True
                    break
            if not name_matched:
                for field in ['jobIds', 'skillIds', 'industryIds']:
                    if field in worker_data and any(
                            nameRelated in str(item).strip().lower() for item in worker_data[field]):
                        matched_workers.append(worker_data)
                        break

        # Check location-related fields in all addresses, including 'address'
        if locationRelated:
            location_matched = False
            if 'addresses' in worker_data and worker_data['addresses'] is not None:
                for address in worker_data['addresses']:
                    for field in ['city', 'state', 'country']:
                        if field in address and locationRelated in str(address[field]).strip().lower():
                            matched_workers.append(worker_data)
                            location_matched = True
                            break
                    if location_matched:
                        break
            if not location_matched and 'address' in worker_data:
                for field in ['city', 'state', 'country']:
                    if field in worker_data['address'] and locationRelated in str(
                            worker_data['address'][field]).strip().lower():
                        matched_workers.append(worker_data)
                        break

    return matched_workers
