# code for deployment
gcloud app deploy

# Upadating List in firestore
db.collection('AppUsers').document(user_id).update({
    'listActiveOrders': firestore.firestore.ArrayUnion([order_data])
})


# Pushing blukers function 2 to github
git push deployment main  

# Pushing blukers function 2 to github
git push origin main 

# Connecting to Redis Server:
### gcloud compute ssh COMPUTE_VM_NAME --zone=ZONE -- -N -L 6379:REDIS_INSTANCE_IP_ADDRESS:6379
1. gcloud compute ssh blukers-vm --zone=us-east1-b -- -N -L 6379:10.167.29.67:6379
2. To confirm Redis Connection: redis-cli ping

## Steps to deploy development branch to production
1. Change Stripe API key to production key
2. Change app.yaml to production (default) 
3. uncomment hardcoded Texas Jobs