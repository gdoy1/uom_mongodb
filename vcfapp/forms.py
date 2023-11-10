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

    ancestral_allele = forms.CharField(
        label='Ancestral allele',
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Only A, C, T, G or N characters allowed",
                'pattern':'[ACTGN]+'
            }
        )
    )

    minor_allele = forms.CharField(
        label='Minor allele',
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Only A, C, T, G or N characters allowed",
                'pattern':'[ACTGN]+'
            }
        )
    )

    strand = forms.ChoiceField(
        required=False,
        label='Strand',
        choices=[
            (None, '--- Select strand ---'),
            ("1", "1"),
            ("-1", "-1")
        ]
    )

    maf = forms.FloatField(
        label='Minor Allele Frequency',
        required=False,
        min_value=0.0,
        max_value=1.0,
        widget=forms.NumberInput(
            attrs={
                "placeholder": "E.g. 0.00345"
            }
        )
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
            ('subsitution', 'substitution'),
            ('tandem_repeat', 'tandem repeat'),
            ('probe', 'probe'), ('translocation', 'translocation'),
            ('tandem_duplication', 'tandem duplication'),
            ('short_tandem_repeat_variation', 'short tandem repeat variation'),
            ('novel_sequence_insertion', 'novel sequence insertion'),
            ('mobile_element_insertion', 'mobile element insertion'),
            ('mobile_element_deletion', 'mobile element deletion'),
            ('loss_of_heterozygosity', 'loss of heterozygosity'),
            ('inversion', 'inversion'),
            ('intrachromosomal_translocation', 'intrachromosomal translocation'),
            ('intrachromosomal_breakpoint', 'intrachromosomal breakpoint'),
            ('interchromosomal_translocation', 'interchromosomal translocation'),
            ('interchromosomal_breakpoint', 'interchromosomal breakpoint'),
            ('duplication', 'duplication'),
            ('copy_number_variation', 'copy number variation'),
            ('copy_number_loss', 'copy number loss'),
            ('copy_number_gain', 'copy number gain'),
            ('complex_substitution', 'complex substitution'),
            ('complex_structural_alteration', 'complex structural alteration'),
            ('complex_chromosomal_rearrangement', 'complex chromosomal rearrangement'),
            ('SVA_insertion', 'SVA insertion'),
            ('SVA_deletion', 'SVA deletion'),
            ('LINE1_insertion', 'LINE1 insertion'),
            ('LINE1_deletion', 'LINE1 deletion'),
            ('HERV_insertion', 'HERV insertion'),
            ('HERV_deletion', 'HERV deletion'),
            ('Alu_insertion', 'Alu insertion'),
            ('Alu_deletion', 'Alu deletion')
        ]
    )

    name = forms.CharField(
        label='Name',
        required=False,
                widget=forms.TextInput(
            attrs={
                "placeholder": "rs1234...",
                "pattern": "(rs[0-9]+)"
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
            ('upstream_gene_variant', 'upstream gene variant'),
            ('transcript_ablation', 'transcript ablation'),
            ('transcript_amplification', 'transcript_amplification'),
            ('feature_elongation', 'feature elongation'),
            ('feature_truncation', 'feature truncation'),
            ('inframe_insertion', 'inframe insertion'),
            ('splice_donor_5th_base_variant', 'splice donor 5th base variant'),
            ('splice_donor_region_variant', 'splice donor region variant'),
            ('splice_polypyrimidine_tract_variant', 'splice polypyrimidine tract variant'),
            ('incomplete_terminal_codon_variant', 'incomplete terminal codon variant'),
            ('start_retained_variant', 'start retained variant'),
            ('NMD_transcript_variant', 'NMD transcript variant'),
            ('non_coding_transcript_variant', 'non coding transcript variant'),
            ('coding_transcript_variant', 'coding transcript variant'),
            ('TFBS_ablation', 'TFBS ablation'),
            ('TFBS_amplification', 'TFBS amplification'),
            ('TF_binding_site_variant', 'TF binding site variant'),
            ('regulatory_region_ablation', 'regulatory region ablation'),
            ('regulatory_region_amplification', 'regulatory region amplification'),
            ('regulatory_region_variant', 'regulatory region variant'),
            ('intergenic_variant', 'intergenic variant'),
            ('sequence_variant', 'sequence variant')
        ]
    )

    synonyms = forms.CharField(
        label='Synonyms',
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Add HGVS notation, separated by commas"
            }
        )
    )

    evidence = forms.CharField(
        label='Evidence',
        required=False,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Add evidence, separated by commas"
            }
        )
    )

    def clean(self):
        # Used to sanitize inputted data to check for invalid inputs
        assembly = self.cleaned_data['assembly']
        chromosome = self.cleaned_data['chromosome']

        start = self.cleaned_data['start']
        end = self.cleaned_data['end']
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
            self.cleaned_data['synonyms'] = []
        if not evidence:
            self.cleaned_data['evidence'] = []

        is_unique = helper.check_single_variant_unique(
            assembly, chromosome, start, end,
            ancestral_allele, minor_allele
        )

        if is_unique != True:
            raise ValidationError(is_unique)

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
                        is_unique = helper.is_var_unique(json_data['name'])
                        if is_unique != True:
                            raise ValidationError(is_unique) 
                    else:
                        raise ValidationError(upload_correct)
                except JSONDecodeError:
                    raise ValidationError(f'Incorrect JSON format...\n{line}')


