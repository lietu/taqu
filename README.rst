.. image:: https://app.fossa.io/api/projects/git%2Bgithub.com%2Flietu%2Ftaqu.svg?type=shield
    :target: https://app.fossa.io/projects/git%2Bgithub.com%2Flietu%2Ftaqu?ref=badge_shield

.. image:: https://travis-ci.org/lietu/taqu.svg?branch=master
    :target: https://travis-ci.org/lietu/taqu

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black

.. image:: https://codecov.io/gh/lietu/taqu/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/lietu/taqu

.. image:: https://sonarcloud.io/api/project_badges/measure?project=lietu-taqu&metric=alert_status
    :target: https://sonarcloud.io/dashboard?id=lietu-taqu

.. image:: https://img.shields.io/github/issues/lietu/taqu
    :target: https://github.com/lietu/taqu/issues
    :alt: GitHub issues

.. image:: https://img.shields.io/pypi/dm/taqu
    :target: https://pypi.org/project/taqu/
    :alt: PyPI - Downloads

.. image:: https://img.shields.io/pypi/v/taqu
    :target: https://pypi.org/project/taqu/
    :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/taqu
    :target: https://pypi.org/project/taqu/
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/badge/License-BSD%203--Clause-blue.svg
    :target: https://opensource.org/licenses/BSD-3-Clause

Python Task Queue system built on Azure Service Bus queues and pydantic models.


What is this?
=============

Lots of systems benefit from having a queue for background tasks, that run independently of e.g. your APIs or other processes. This can help e.g. by enhancing your API performance, limiting the effects of traffic peaks, as well as scaling out with parallel processing of various things.

The defacto standard for Python is Celery + RabbitMQ, but hosting RabbitMQ is another liability and not always the most fun experience, and Celery doesn't support ``asyncio`` yet. Fully hosted solutions such as the Azure Service Bus help you get off the ground faster, with less things to worry about, and can allow you to save on costs as well.

Primarily intended for use with ``asyncio`` (from ``taqu.aio`` module), but works with non-async code just as well (using imports from the ``taqu`` module).

Supports all the basic things you could need:

 - Fast insertion of tasks to queue
 - Async task processing
 - Easy to scale workers
 - Retry logic - if there's an uncaught exception the task will automatically be put back in the queue
 - Clean shutdown on Ctrl+C (waits until tasks finish processing)


License
-------

Licensing is important. This project itself uses BSD 3-clause license, but e.g. Azure library for Storage Bus and other such libraries used by it may have their own licenses.

For more information check the `LICENSE <https://github.com/lietu/taqu/blob/master/LICENSE>`_ -file.


Getting started
===============

In the `Azure Portal <https://portal.azure.com>`_ set up a new Service Bus (any tier is fine), and then a queue in it. You probably want to enable partitioning, maybe also dead-lettering. Then you'll want to get the access credentials for your code. Ensure you've got the `Azure CLI <https://docs.microsoft.com/en-us/cli/azure/install-azure-cli?view=azure-cli-latest#install>`_ installed and then run:

.. code-block:: bash

    az login  # Ensure you're logged in to Azure
    az account list  # List subscriptions
    az account set --subscription <subscriptionId>  # Set active subscription

    az servicebus namespace authorization-rule keys list \
        --resource-group <rgName> \
        --namespace-name <namespace> \
        --name RootManageSharedAccessKey \
        --query primaryConnectionString \
        --output tsv

Also you'll need the Taqu library installed, e.g. for use with the Azure:

.. code-block:: bash

    pip install taqu[azure]

Then, you can set up your worker, here's an example ``worker.py`` that you can just run with ``python worker.py``:

.. code-block:: python

    import asyncio

    from taqu.aio import TaquAzureWorker
    from pydantic import BaseModel

    CONNECTION_STRING = "..."

    worker = TaquAzureWorker(CONNECTION_STRING)


    class CreateUser(BaseModel):
        username: str

    async def create_user(user: CreateUser):
        print(user.username)

    worker.register(create_user)
    worker.run()

With the worker in place, you can create a client and send some tasks

.. code-block:: python

    from taqu import TaquAzureClient
    from pydantic import BaseModel

    CONNECTION_STRING = "..."

    taqu = TaquAzureClient(CONNECTION_STRING)


    class CreateUser(BaseModel):
        username: str


    taqu.add_task(CreateUser(username="my_new_username"))

You can also check out the `examples <https://github.com/lietu/taqu/tree/master/examples>`_.


Contributing
============

This project is run on GitHub using the issue tracking and pull requests here. If you want to contribute, feel free to `submit issues <https://github.com/lietu/taqu/issues>`_ (incl. feature requests) or PRs here.

To test changes locally ``python setup.py develop`` is a good way to run this, and you can ``python setup.py develop --uninstall`` afterwards (you might want to also use the ``--user`` flag).


Financial support
=================

This project has been made possible thanks to `Cocreators <https://cocreators.ee>`_ and `Lietu <https://lietu.net>`_. You can help us continue our open source work by supporting us on `Buy me a coffee <https://www.buymeacoffee.com/cocreators>`_.

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
   :target: https://www.buymeacoffee.com/cocreators
