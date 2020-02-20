
from .models import *
from .utils import *
from .agent_utils import *
from .wallet_utils import *
from .indy_utils import *


def user_provision(user, raw_password):
    """
    Create a new user agent and associate with the user
    """

    agent_name = get_user_wallet_name(user.email)

    # save everything to our database
    agent = initialize_and_provision_agent(
            agent_name, 
            raw_password
        )
    agent.save()
    user.agent = agent
    user.save()

    return user


def org_provision(org, raw_password, org_role=None):
    """
    Create a new org agent and associate to the org
    """

    agent_name = get_org_wallet_name(org.org_name)
    #res = create_agent(agent_name, raw_password)
    #if res != 0:
    #    raise Exception("Error agent create failed: " + str(res))

    # create a did for this org
    did_seed = calc_did_seed(agent_name)

    # save everything to our database
    agent = initialize_and_provision_agent(
            agent_name, 
            raw_password,
            did_seed=did_seed
        )
    agent.save()
    org.agent = agent
    org.save()

    # if the org has a role, check if there are any schemas associated with that role
    if org_role:
        try:
            start_agent(org.agent)

            role_schemas = IndySchema.objects.filter(roles=org_role).all()
            for schema in role_schemas:
                creddef = create_creddef(org.agent, schema, schema.schema_name + '-' + org.agent.agent_name, schema.schema_template)
        finally:
            stop_agent(org.agent)

    return org


def org_signup(user, raw_password, org_name, org_attrs={}, org_relation_attrs={}, org_role=None, org_ico_url=None):
    """
    Helper method to create and provision a new org, and associate to the current user
    """
    
    if not org_ico_url:
        org_ico_url = 'http://robohash.org/456'

    org = get_aries_settings_model('ARIES_ORGANIZATION_MODEL').objects.create(org_name=org_name, role=org_role, ico_url=org_ico_url, **org_attrs)

    org = org_provision(org, raw_password, org_role)

    # associate the user with the org
    relation = get_aries_settings_model('ARIES_ORG_RELATION_MODEL').objects.create(org=org, user=user, **org_relation_attrs)
    relation.save()

    return org

