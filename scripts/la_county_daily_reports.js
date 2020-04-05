const cheerio = require('cheerio');
const request = require('request');
const lacounty_url = 'http://publichealth.lacounty.gov/media/Coronavirus/locations.htm'; 
request(lacounty_url, function (error, response, html) {
  if (!error && response.statusCode == 200) {
    const $ = cheerio.load(html);
    const data = $('tbody tr').map((ii, obj) => [$(obj).find('td:nth-child(1)').text(), $(obj).find('td:nth-child(2)').text(), $(obj).find('td:nth-child(3)').text()].join(','));
    var i;
    for (i = 0; i < parseInt(data['length']); i++) {
      console.log(data[i.toString()]);
    }
  }
});
