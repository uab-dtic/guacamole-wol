#!/usr/bin/perl -w
#

#
# export-dhcpd-reservations.pl -- v0.01 (2015/05/20)
# Exports dhcpd.conf reservations to a CSV (suitable for migration)
#
# Import from STDIN, export to STDOUT
# Example: cat dhcpd.conf | perl export-dhcpd-reservations.pl > output.csv
#
# Copyright (C) 2015 Jelle Hillen (visit: http://www.blackmanticore.com/)
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#

#


package ExportDhcpdReservations;

use warnings 'all';
use strict;

sub trim($) {
	my $s = shift;
	$s =~ s/^\s+//;
	$s =~ s/\s+$//;
	return $s;
}

sub unquote($) {
	my $s = shift;
	$s =~ s/\"//g;
	return $s;
}

sub quote($) {
	my $s = shift;
	return "\"$s\"";
}

our $host = 0;
our $exported = 0;
$_ = "" for our ($resname,$ip4addr,$macaddr,$dnsname,$options,$bootfile);
print "reservation_name\thardware_address\tipv4_address\tdns_hostname\toptions\tbootfile\n";
while (<STDIN>) {
	chomp;
	$_ = &trim($_);
	if (/^group\s+([^#\{]+)\s*\{/) {
		print "$1\t\t\t\t\t\n";
	}
	elsif (/^host\s+([^#\{\s]+)\s*\{/) { # find host reservation entry
		$resname = $1;
		$host = 1;
	}
	elsif ($host) { # inside host reservation entry
		if (/^hardware\s+ethernet\s+([0-9a-fA-F\:]{17})\;/) { # find MAC address
			$macaddr = lc($1);
			#$macaddr =~ s/\://g;
		}
		elsif (/^fixed\-address\s+([\d\.]+)\;/) { # find fixed IPv4
			$ip4addr = $1;
		}
		elsif (/^ddns\-hostname\s+([^#\;]+)\;/) { # find DNS-name
			$dnsname = &unquote($1);
		}
		elsif (/^option\s+([^\#\;]+)\;/) { # find options for this reservation
			$options = $1;
			if ($options =~ /^host\-name\s+([^#]+)/ && $dnsname eq "") {
				$dnsname = &unquote($1);
				$options = "";
			}
		}
		elsif (/^filename\s+([^\#\;]+)\;/) { # find boot file for this reservation
			$bootfile = &unquote($1);
		}
		elsif (/^\}/) { # end of host reservation, write to file
			#print &quote($resname)."\t".&quote($macaddr)."\t".&quote($ip4addr)."\t".&quote($dnsname)."\t".&quote($options)."\t".&quote($bootfile)."\n";
			print $resname.";".$macaddr.";".$ip4addr.";".$dnsname.";".$options.";".$bootfile."\n";
			$resname = "";
			$ip4addr = "";
			$macaddr = "";
			$dnsname = "";
			$options = "";
			$bootfile = "";
			$host = 0;
			++$exported;
		}
	}
}
print STDERR "\n\nExported: $exported entries\n\n";
