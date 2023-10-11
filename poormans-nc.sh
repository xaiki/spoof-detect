#!/bin/sh

PORT=1234
while true; do
      perl -MIO::Socket::INET -ne "BEGIN{\$l=IO::Socket::INET->new(
        LocalPort=>$PORT,Proto=>\"tcp\",Listen=>5,ReuseAddr=>1);
          \$l=\$l->accept} die"
      ps auxf | grep geckodriver | grep -v sh | grep -v grep | awk "{print $2}" | xargs -n1 kill
      sleep 1
done
