#!/usr/lib/python
#-*- coding: utf-8 -*-

'''This module define four classes: GeneralVcf, FbVcf, GATKvcf, SBVcf.
Designing last three classes respectively because DP, Acount, Rcount
are in different vcf files with different positions.'''

class GeneralVcf:
    '''GeneralVcf is used for any vcf files, you can get chr, pos, Rbase,
Abase, qual(float), GenoType attributes because these items in different vcf
files at the same positons. Caveat: the raw vcf file from samtools may
not contain the last colum which include GenoType info, so you should
filter those lines firstly, then use this class.'''
    def chr(self, line):
        return line.split()[0]
    def pos(self, line):
        return int(line.split()[1])
    def Rbase(self, line):
        return line.split()[3]
    def Abase(self, line):
        return line.split()[4]
    def qual(self, line):
        return line.split()[5]
    def GenoType(self, line):
        return line.split()[-1].split(':')[0]

class FbVcf(GeneralVcf):
    '''This class is special for vcf file generated by freebayse. Caveat:
in freebayes vcf files, DP(int) sometimes is not equal with AO+RO....  and the
Acount(int) of freebayes may have mutiple figure, for example:
Rcount(int):100, A1count:30, A2count:30. the genotype of this site called 1/2,
the last colum like this:
1/2:23:2:68:3,18:117,637:-10,-10,-10,-5.00407,0,-7.36222
to tacke this situation, I temporary pick the biger one as Acount.'''
    def DP(self, line):
        return int(line.split()[-1].split(':')[1])
    def Rcount(self, line):
        return int(line.split()[-1].split(':')[2])
    def Acount(self, line):
        if len(line.split()[-1].split(':')[4]) == 1:
            return int(line.split()[-1].split(':')[4])
        else:
            return max([int(i) for i in line.split()[-1].split(':')[4].split(',')])
    def VariantType(self, line):
        self.line = line
        infocolumn = self.line.split()[7]
        ele = infocolumn.split(';')
        dic1 = {}
        for i in ele:
            dic1[i.split('=')[0]]=i.split('=')[1]
        if 'TYPE' in dic1:
            return dic1['TYPE']
        else:
            return None

class GATKVcf(GeneralVcf):
    '''This class is only used for GATK vcf files. the raw gatk vcf files may
contain some lines which lack of DP of AO items, so you'd better fileter them
first.'''
    def __init__(self, line):
        GeneralVcf.__init__(self, line)
        if len(line.split()[-1].split(':')) == 5:
            self.DP = int(line.split()[-1].split(':')[2])
            self.Rcount = int(line.split()[-1].split(':')[1].split(',')[0])
            self.Acount = int(line.split()[-1].split(':')[1].split(',')[1])
        else:
            print "you'd better filter the line which lack of core infos..."
            self.DP = 0
            self.Rcount = 0
            self.Rcount = 0

class SBVcf(GeneralVcf):
    '''This class is used for samtools vcf files.'''
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
            print "you'd better filter the line which lack of core infos..."
            self.Rcount = 0
            self.Acount = 0
            self.DP = 0

if __name__ == '__main__':
    print  'just import these classes to use.'
