import json
from json.decoder import JSONDecodeError
from django import forms
from django.core.exceptions import ValidationError
from .utils import VcfAppUtils

helper = VcfAppUtils()

class SingleVariantForm(forms.Form):

    assembly = forms.ChoiceField(
        label='Genome assembly',
        required=True,
        choices=[
            (None, "--- Select a genome assembly ---"),
            ("GRCh38", "GRCh38"),
            ("GRCh37", "GRCh37")
        ]
    )

    chromosome = forms.ChoiceField(
        label='Chromosome',
        required=True,
        choices=[
            (None, "--- Select a chromosome ---"),
            ("1", "chr1"), ("2", "chr2"),
            ("3", "chr3"), ("4", "chr4"),
            ("5", "chr5"), ("6", "chr6"),
            ("7", "chr7"), ("8", "chr8"),
            ("9", "chr9"), ("10", "chr10"),
            ("11", "chr11"), ("12", "chr12"),
            ("13", "chr13"), ("14", "chr14"),
            ("15", "chr15"), ("16", "chr16"),
            ("17", "chr17"), ("18", "chr18"),
            ("19", "chr19"), ("20", "chr20"),
            ("21", "chr21"), ("22", "chr22"),
            ("X", "chrX"), ("Y", "chrY")
        ]
    )

    start = forms.IntegerField(
        label='Start coordinate',
        required=True,
        min_value=0
    )

    end = forms.IntegerField(
        label='End coordinate',
        required=True,
        min_value=0
    )

    strand = forms.ChoiceField(
        required=False,
        label='Strand',
        choices=[
            (None, '--- Select strand'),
            ("1", "1"),
            ("-1", "-1")
        ]
    )

    maf = forms.FloatField(
        label='Minor Allele Frequency',
        required=False,
        min_value=0.0,
        max_value=1.0
    )

    ambiguity = forms.ChoiceField(
        label='Ambiguity',
        required=False,
        choices=[
            (None, '--- Select ambiguity ---'),
            ('A', 'A'), ('C', 'C'),
            ('G', 'G'), ('T', 'T'),
            ('R', 'R'), ('Y', 'Y'),
            ('S', 'S'), ('W', 'W'),
            ('K', 'K'), ('B', 'B'),
            ('D', 'D'), ('H', 'H'),
            ('V', 'V'), ('N', 'N'),
            ('.', '.')
        ]
    )

    var_class = forms.ChoiceField(
        label='Variant class',
        required=False,
        choices=[
            (None, '--- Select variant class ---'),
            ('SNP', 'SNP'), ('deletion', 'deletion'),
            ('indel', 'indel'), ('insertion', 'insertion'),
            ('sequence_alteration', 'sequence alteration'),
            ('somatic_SNV', 'somatic SNV'),
            ('somatic_deletion', 'somatic deletion'),
            ('subsitution', 'substitution'), ('tandem_repeat', 'tandem repeat')
        ]
    )

    name = forms.CharField(
        label='Name',
        required=False,
                widget=forms.TextInput(
            attrs={
                "placeholder": "rs...",
                "pattern": "(rs[0-9]+)"
            }
        )
    )

    ancestral_allele = forms.CharField(
        label='Ancestral allele',
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. 'A'",
                'pattern':'[ACTGN]+'
            }
        )
    )

    minor_allele = forms.CharField(
        label='Minor allele',
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "e.g. 'G'",
                'pattern':'[ACTGN]+'
            }
        )
    )

    most_severe_consequence = forms.ChoiceField(
        label='Most severe consequence',
        required=False,
        choices=[
            (None, '--- Select a consequence type ---'),
            ('3_prime_UTR_variant','3 prime UTR variant'),
            ('5_prime_UTR_variant','5 prime UTR variant'),
            ('coding_sequence_variant', 'coding sequence variant'),
            ('downstream_gene_variant', 'downstream gene variant'),
            ('frameshift_variant', 'frameshift variant'),
            ('inframe_deletion', 'inframe deletion'),
            ('intron_variant', 'intron variant'),
            ('mature_miRNA_variant', 'mature miRNA variant'),
            ('missense_variant', 'missense variant'),
            ('non_coding_transcript_exon_variant', 'non coding transcript exon variant'),
            ('protein_altering_variant', 'protein altering variant'),
            ('splice_acceptor_variant', 'splice acceptor variant'),
            ('splice_donor_variant', 'splice donor variant'),
            ('splice_region_variant', 'splice region variant'),
            ('start_lost', 'start lost'),
            ('stop_gained', 'stop gained'),
            ('stop_lost', 'stop lost'),
            ('stop_retained_variant', 'stop retained variant'),
            ('synonymous_variant', 'synonymous variant'),
            ('upstream_gene_variant', 'upstream gene variant')
        ]
    )

    synonyms = forms.CharField(
        label='Synonyms',
        required=False
    )

    evidence = forms.CharField(
        label='Evidence',
        required=False
    )

    def clean(self):
        # Used to sanitize inputted data to check for invalid inputs
        assembly = self.cleaned_data['assembly']
        chromosome = self.cleaned_data['chromosome']

        strand = self.cleaned_data['strand']
        maf = self.cleaned_data['maf']
        ambiguity = self.cleaned_data['ambiguity']
        var_class = self.cleaned_data['ambiguity']
        name = self.cleaned_data['name']
        ancestral_allele = self.cleaned_data['ancestral_allele']
        minor_allele = self.cleaned_data['minor_allele']
        most_severe_consequence = self.cleaned_data['most_severe_consequence']
        synonyms = self.cleaned_data['synonyms']
        evidence = self.cleaned_data['evidence']

        if None in (assembly, chromosome):
        # Check both assembly and chromosome included
            raise ValidationError(
                "Please ensure assembly and chromosome are entered"
            )

        if not strand:
            self.cleaned_data['strand'] = None
        if not maf:
            self.cleaned_data['maf'] = None
        if not ambiguity:
            self.cleaned_data['ambiguity'] = None
        if not var_class:
            self.cleaned_data['var_class'] = None
        if not name:
            self.cleaned_data['name'] = None
        if not ancestral_allele:
            self.cleaned_data['ancestral_allele'] = None
        if not minor_allele:
            self.cleaned_data['minor_allele'] = None
        if not most_severe_consequence:
            self.cleaned_data['most_severe_consequence'] = None
        if not synonyms:
            self.cleaned_data['synonyms'] = None
        if not evidence:
            self.cleaned_data['evidence'] = None

        return self.cleaned_data


class UploadForm(forms.Form):
    file = forms.FileField()

    def clean(self):
        upload_file = self.cleaned_data['file'].file.getvalue()
        for line in upload_file.decode('utf-8').split('\n'):
            if line.strip():
                try:
                    json_data = json.loads(line)
                    # check if required keys are filled
                    # check if name already exists in collection
                    upload_correct = helper.check_upload_file(json_data)
                    if upload_correct:
                        try:
                            assembly = json_data['mappings'][0]['assembly_name']
                            chr = json_data['mappings'][0]['seq_region_name']
                            start = json_data['mappings'][0]['start']
                            end = json_data['mappings'][0]['end']
                            ref = json_data['ancestral_allele']
                            alt = json_data['minor_allele']
                            is_unique = helper.is_var_unique(
                                assembly,
                                chr,
                                start,
                                end,
                                ref,
                                alt)
                            if is_unique != True:
                                raise ValidationError(is_unique)
                        except KeyError:
                            raise ValidationError(f'Error... missing field\n{json_data}')
                    else:
                        raise ValidationError(upload_correct)
                except JSONDecodeError:
                    raise ValidationError(f'Incorrect JSON format...\n{line}')

