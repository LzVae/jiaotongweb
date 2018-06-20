CREATE TABLE `chart_chartdate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `year` int(11) NOT NULL,
  `month` int(11) NOT NULL,
  `day` int(11) NOT NULL,
  `direction` int(11) NOT NULL,
  `Xaxisa` int(11) NOT NULL,
  `Xaxisb` int(11) NOT NULL,
  `Yaxis` int(11) NOT NULL,
  `Alane` int(11) NOT NULL,
  `Blane` int(11) NOT NULL,
  `Clane` int(11) NOT NULL,
  `Dlane` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
