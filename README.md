# A auctions website where users can list items and bid on others' listings

## To run the auctions locally

1. Clone the repo `git clone https://github.com/nhhoang-tony/Ebay.git`

2. Ensure you have Python installed on your system. If not, follow this guide to install `https://www.python.org/downloads/`

3. Run `pip install -r requirements.txt` to install the project dependencies.

4. Run `echo $TZ > /etc/timezone` and `ln -snf /usr/share/zoneinfo/$TZ /etc/localtime` to set up timezone

5. Run `python manage.py runserver` to start the auctions
