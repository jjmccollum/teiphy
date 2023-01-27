#!/usr/bin/env python3

"""
BEAST XML template string
"""
beast_template = """
<beast version="2.7" namespace="beast.pkgmgmt:beast.base.core:beast.base.inference:beast.base.inference.distribution:beast.base.inference.util:beast.base.evolution:beast.base.evolution.alignment:beast.base.evolution.datatype:beast.base.evolution.tree:beast.base.evolution.tree.coalescent:beast.base.evolution.branchratemodel:beast.evolution.nuc:beast.base.evolution.operator:beast.base.inference.operator:beast.base.evolution.sitemodel:beast.base.evolution.substitutionmodel:beast.base.evolution.likelihood">
    <data spec="Alignment" id="alignment" dataType="standard" statecount="{nsymbols}">
        <!-- Start sequences -->
        <!-- End sequences -->
        <userDataType spec="StandardData" nrOfStates="{nsymbols}">
            <!-- Start charstatelabels -->
            <!-- End charstatelabels -->
        </userDataType>
    </data>
    <tree spec="Tree" id="tree">
        <trait spec="TraitSet" traitname="date" units="year" value="{date_map}">
            <taxa spec="TaxonSet" id="taxa" alignment="@alignment"/>
        </trait>
        <taxonset idref="taxa"/>
    </tree>
    <birthDeathSkylineModel spec="bdsky.evolution.speciation.BirthDeathSkylineModel" id="birthDeath" tree="@tree">
        <parameter spec="parameter.RealParameter" id="origin" name="origin" lower="{date_span}" upper="Infinity" value="{date_span}"/>
        <parameter spec="parameter.RealParameter" id="reproductiveNumber" name="reproductiveNumber" lower="0.0" upper="Infinity" value="2.0"/>
        <parameter spec="parameter.RealParameter" id="becomeUninfectiousRate" name="becomeUninfectiousRate" lower="0.0" upper="Infinity" value="1.0"/>
        <parameter spec="parameter.RealParameter" id="samplingProportion" name="samplingProportion" lower="0.0" upper="1.0" value="0.01"/>
    </birthDeathSkylineModel>
    <branchRateModel spec="StrictClockModel" id="strictClock">
		<parameter dimension="1" id="clock.rate" name="clock.rate" lower="0.0" upper="100.0" value="0.1"/>
	</branchRateModel>
    <!-- The chainLength attribute should be increased to a large number (e.g., 20000000) for non-test runs -->
    <run spec="MCMC" id="mcmc" chainLength="100000">
        <state spec="State" id="state" storeEvery="5000">
            <stateNode idref="tree"/>
            <stateNode idref="origin"/>
			<stateNode idref="becomeUninfectiousRate"/>
			<stateNode idref="samplingProportion"/>
			<stateNode idref="reproductiveNumber"/>
			<stateNode idref="clock.rate"/>
            <!-- Start intrinsic parameters -->
            <!-- End intrinsic parameters -->
            <!-- Start transcriptional parameters -->
            <!-- End transcriptional parameters -->
            <!-- We include a "default" rate fixed at 1 that corresponds to (unlikely) transitions with no transcriptional explanation.
            All other rates in the substitution matrices will be estimated relative to this.
            If no other transcriptional rate parameters are specified, then the substitution matrices will correspond to those of the Lewis Mk model. -->
            <parameter spec="parameter.RealParameter" id="default_rate" name="stateNode" value="1.0" estimate="false"/>
        </state>
        <distribution spec="CompoundDistribution" id="posterior">
            <distribution spec="CompoundDistribution" id="prior">
                <!-- Priors for the Birth-Death Skyline model -->
                <distribution spec="CompoundDistribution" id="bdLikelihood">
                    <distribution idref="birthDeath"/>
                </distribution>
                <distribution spec="Prior" id="originPrior" x="@origin">
                    <distr spec="LogNormalDistributionModel" M="0.0" S="1.0" offset="{date_span}"/>	
                </distribution>
                <distribution spec="Prior" id="samplingProportionPrior" x="@samplingProportion">
                    <distr spec="Beta" alpha="1.0" beta="1.0" offset="0.0"/>
                </distribution>
                <distribution spec="Prior" id="reproductiveNumberPrior" x="@reproductiveNumber">
                    <distr spec="LogNormalDistributionModel" M="0.0" S="1.0"/>
                </distribution>
                <distribution spec="Prior" id="becomeUninfectiousRatePrior" x="@becomeUninfectiousRate">
                    <distr spec="LogNormalDistributionModel" M="0.0" S="1.0"/>
                </distribution>
            </distribution>
            <distribution spec="CompoundDistribution" id="likelihood" useThreads="true">
                <!-- Start character distributions -->
                <!-- End character distributions -->
            </distribution>
        </distribution>
        <!-- Operators for the Birth-Death Skyline model -->
        <operator spec="ScaleOperator" id="bdskySerialTreeScaler" scaleFactor="0.5" tree="@tree" weight="3.0"/>
        <operator spec="ScaleOperator" id="bdskySerialTreeRootScaler" rootOnly="true" scaleFactor="0.5" tree="@tree" weight="3.0"/>
        <operator spec="beast.base.evolution.operator.Uniform" id="bdskySerialUniformOperator" tree="@tree" weight="30.0"/>
        <operator spec="SubtreeSlide" id="bdskySerialSubtreeSlide" tree="@tree" weight="15.0"/>
        <operator spec="Exchange" id="bdskySerialNarrow" tree="@tree" weight="0.0"/>
        <operator spec="Exchange" id="bdskySerialWide" isNarrow="false" tree="@tree" weight="3.0"/>
        <operator spec="WilsonBalding" id="bdskySerialWilsonBalding" tree="@tree" weight="3.0"/>
        <operator spec="ScaleOperator" id="originScaler" parameter="@origin" weight="10.0"/>
        <operator spec="ScaleOperator" id="becomeUninfectiousRateScaler" parameter="@becomeUninfectiousRate" weight="2.0"/>
        <operator spec="ScaleOperator" id="reproductiveNumberScaler" parameter="@reproductiveNumber" weight="10.0"/>
        <operator spec="ScaleOperator" id="samplingProportionScaler" parameter="@samplingProportion" weight="10.0"/>
        <operator spec="UpDownOperator" id="updownBD" scaleFactor="0.75" weight="2.0">
            <up idref="reproductiveNumber"/>
            <down idref="becomeUninfectiousRate"/>
        </operator>
        <!-- Operators for the clock model -->
        <operator id="tree_updown" spec="UpDownOperator" scaleFactor=".75" weight="10">
			<up idref="tree"/>
			<down idref="clock.rate"/>
		</operator>
		<operator id="clock.rate_Scaler" spec="ScaleOperator" scaleFactor=".75" weight="1" parameter="@clock.rate" />
        <!-- Start transcriptional rate operators -->
        <!-- End transcriptional rate operators -->
        <logger spec="Logger" id="tracelog" fileName="beast.log" logEvery="1000" model="@posterior" sanitiseHeaders="true" sort="smart">
            <log idref="posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
            <log spec="TreeHeightLogger" id="treeHeight" tree="@tree"/>
            <log idref="birthDeath"/>
            <log idref="origin"/>
            <log idref="becomeUninfectiousRate"/>
            <log idref="reproductiveNumber"/>
            <log idref="samplingProportion"/>
            <log spec="RateStatistic" id="rate" branchratemodel="@strictClock" tree="@tree"/>
            <!-- Start transcriptional rate loggers -->
            <!-- End transcriptional rate loggers -->
        </logger>
        <logger spec="Logger" id="screenlog" logEvery="1000">
            <log idref="posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
        </logger>
        <logger spec="Logger" id="treelog" fileName="$(tree).trees" logEvery="1000" mode="tree">
            <log spec="TreeWithMetaDataLogger" id="treeWithMetaDataLogger" branchratemodel="@strictClock" tree="@tree"/>
        </logger>
        <operatorschedule spec="OperatorSchedule" id="operatorSchedule"/>
        <logger id="ancestralStateLogger" fileName="$(tree).ancestral.trees" logEvery="10000" mode="tree">
            <!-- Start character ancestral state loggers -->
            <!-- End character ancestral state loggers -->
        </logger>
    </run>
</beast>
"""

"""
BEAST XML sequence template string
"""
sequence_template = """
<sequence spec="Sequence" taxon="{wit_id}" uncertain="true" value="{sequence}"/>
"""

"""
BEAST XML charstatelabels template string
"""
charstatelabels_template = """
<charstatelabels spec="UserDataType" characterName="{vu_id}" codeMap="{code_map}" states="{nstates}" value="{rdg_texts}"/>
"""

"""
BEAST XML transcriptional rate parameter template string
"""
transcriptional_rate_parameter_template = """
<parameter spec="parameter.RealParameter" id="{transcriptional_category}_rate" name="stateNode" lower="1.0" upper="Infinity" value="{value}" estimate="{estimate}"/>
"""

"""
BEAST XML distribution template string
"""
distribution_template = """
<distribution spec="TreeLikelihood" id="morphTreeLikelihood.character{vu_ind}" useAmbiguities="true" useTipLikelihoods="true" tree="@tree">
    <data spec="FilteredAlignment" id="filter{vu_ind}" data="@alignment" filter="{vu_ind}">
        <userDataType spec="StandardData" id="morphDataType.character{vu_ind}" nrOfStates="{nstates}"/>
    </data>
    <siteModel spec="SiteModel" id="morphSiteModel.character{vu_ind}">
        <parameter spec="parameter.RealParameter" id="mutationRate.character{vu_ind}" name="mutationRate" value="1.0" estimate="false"/>
        <parameter spec="parameter.RealParameter" id="gammaShape.character{vu_ind}" name="shape" value="1.0" estimate="false"/>
        <substModel spec="GeneralSubstitutionModel" id="substModel.character{vu_ind}">
            <!-- Equilibrium frequencies -->
            <frequencies spec="Frequencies" id="equilibriumfreqs.character{vu_ind}">
                <frequencies spec="parameter.RealParameter" id="equilibriumfrequencies.character{vu_ind}" value="{equilibrium_frequencies}" estimate="false"/>
            </frequencies>
            <parameter spec="parameter.CompoundValuable" id="rates.character{vu_ind}" name="rates">
                <!-- Start rate vars -->
                <!-- End rate vars -->
            </parameter>
        </substModel>
    </siteModel>
    <!-- root frequencies -->
    <rootFrequencies spec="Frequencies" id="rootfreqs.character{vu_ind}">
        <frequencies spec="parameter.RealParameter" id="rootfrequencies.character{vu_ind}" value="{root_frequencies}" estimate="false"/>
    </rootFrequencies>
    <branchRateModel idref="strictClock"/>
</distribution>
"""

"""
BEAST XML single rate variable template
"""
var_template = """
<var idref="{transcriptional_category}_rate"/>
"""

"""
BEAST XML multiple rate variable template (for sum of rate parameters)
"""
rpn_calculator_template = """
<var spec="RPNcalculator" expression="{expression}"/>
"""

"""
BEAST XML parameter template (for input to RPNcalculator)
"""
rpn_calculator_parameter_template = """
<parameter idref="{transcriptional_category}_rate"/>
"""

"""
BEAST XML operator template for rate variables
"""
transcriptional_rate_parameter_operator_template = """
<operator id="scaler.{transcriptional_category}_rate" spec="ScaleOperator" scaleFactor="0.5" weight="1" parameter="@{transcriptional_category}_rate"/>
"""

"""
BEAST XML log template for rate variables
"""
transcriptional_rate_parameter_log_template = """
<log idref="{transcriptional_category}_rate"/>
"""

"""
BEAST XML log template for individual sites
"""
character_log_template = """
<log spec="beastlabs.evolution.likelihood.AncestralStateLogger" id="morphTreeLikelihood.character{vu_ind}.anclogger" data="@filter{vu_ind}" taxonset="@taxa" siteModel="@morphSiteModel.character{vu_ind}" branchRateModel="@strictClock" tree="@tree" useAmbiguities="true" useTipLikelihoods="true"/>
"""
