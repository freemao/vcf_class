#!/usr/lib/python

#from optparse import OptionParser

#msg_usage = 'just import these classes'
#descr ='''Define four classes. The first one GeneralVcf is used for any vcf
#files, you can get chr, pos, Rbase, Abase, genotype attributes because these items
#in different vcf files at the same positons. Caveat: the raw vcf file from samtools
#don't contain the last colum which include genotype info, so you should filter those
#lines firstly, then use this class.The second one is special for vcf file generated
#by freebayse. Caveat: in freebayes vcf files, DP sometimes is not equal with
#AO+RO....  The third one is only for GATK vcf files and the last class is
#used for samtools vcf files. Designing these three classes respectively because
#DP, Acount, Rcount are in different vcf files with different positions.
#'''

#optparser = OptionParser(usage = msg_usage, description = descr)
#options, args = optparser.parse_args()

class GeneralVcf:
    def __init__(self, line):
        self.chr = line.split()[0]
        self.pos = int(line.split()[1])
        self.Rbase = line.split()[3]
        self.Abase = line.split()[4]
        self.genotype = line.split()[-1].split(':')[0]

class FbVcf(GeneralVcf):
    '''the A count of freebayes may have mutiple figure, for example
    Rcount:100, A1count:30, A2count:30. the genotype of this site called 1/2,
    the last colum like this:
    1/2:23:2:68:3,18:117,637:-10,-10,-10,-5.00407,0,-7.36222
    to tacke this situation, I temporary pick the biger one as Acount.
    '''

    def __init__(self, line):
        GeneralVcf.__init__(self, line)
        self.DP = int(line.split()[-1].split(':')[1])
        self.Rcount = int(line.split()[-1].split(':')[2])
        if len(line.split()[-1].split(':')[4]) == 1:
            self.Acount = int(line.split()[-1].split(':')[4])
        else:
            self.Acount = max([int(i) for i in line.split()[-1].split(':')[4].split(',')])

class GATKVcf(GeneralVcf):
    def __init__(self, line):
        GeneralVcf.__init__(self, line)
        self.DP = int(line.split()[-1].split(':')[2])
        self.Rcount = int(line.split()[-1].split(':')[1].split(',')[0])
        self.Acount = int(line.split()[-1].split(':')[1].split(',')[1])

class SBVcf(GeneralVcf):
    def __init__(self, line):
        GeneralVcf.__init__(self, line)
        self.info_dict = {}
        self.items = line.split()[7].split(';')
        for k in self.items:
            self.info_dict[k.split('=')[0]] = k.split('=')[1]
        if 'DP4' in self.info_dict:
            self.Rcount = int(self.info_dict['DP4'].split(',')[0]) + \
int(self.info_dict['DP4'].split(',')[1])
            self.Acount = int(self.info_dict['DP4'].split(',')[2]) + \
int(self.info_dict['DP4'].split(',')[3])
            self.DP = self.Rcount + self.Acount
        else:
            self.Rcount = 'noRecord'
            self.Acount = 'noRecord'
            self.DP = 'noRecord'
