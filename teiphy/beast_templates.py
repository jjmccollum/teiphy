#!/usr/bin/env python3

"""
BEAST XML template string
"""
beast_template = """
<beast version="2.7" namespace="beast.pkgmgmt:beast.base.core:beast.base.inference:beast.base.evolution.alignment:beast.base.evolution.datatype:beast.base.evolution.tree:beast.base.evolution.tree.coalescent:beast.base.inference.util:beast.evolution.nuc:beast.base.evolution.operator:beast.base.inference.operator:beast.base.evolution.sitemodel:beast.base.evolution.substitutionmodel:beast.base.evolution.likelihood">
    <data spec="Alignment" id="alignment" dataType="standard" statecount="{nsymbols}">
        <!-- Start sequences -->
        <!-- End sequences -->
        <userDataType spec="StandardData">
            <!-- Start charstatelabels -->
            <!-- End charstatelabels -->
        </userDataType>
    </data>
    <map name="Uniform">beast.math.distributions.Uniform</map>
    <map name="Exponential">beast.math.distributions.Exponential</map>
    <map name="LogNormal">beast.math.distributions.LogNormalDistributionModel</map>
    <map name="Normal">beast.math.distributions.Normal</map>
    <map name="Beta">beast.math.distributions.Beta</map>
    <map name="Gamma">beast.math.distributions.Gamma</map>
    <map name="LaplaceDistribution">beast.math.distributions.LaplaceDistribution</map>
    <map name="prior">beast.math.distributions.Prior</map>
    <map name="InverseGamma">beast.math.distributions.InverseGamma</map>
    <map name="OneOnX">beast.math.distributions.OneOnX</map>
    <tree spec="Tree" id="tree">
        <trait spec="TraitSet" traitname="date" units="year" value="{date_map}">
            <taxa spec="TaxonSet" alignment="@alignment"/>
        </trait>
    </tree>
    <BirthDeathSkylineModel spec="bdsky.evolution.speciation.BirthDeathSkylineModel" id="birthDeath" tree="@tree">
        <parameter spec="parameter.RealParameter" id="reproductiveNumber" name="reproductiveNumber" lower="0.0" upper="Infinity" value="2.0"/>
        <parameter spec="parameter.RealParameter" id="becomeUninfectiousRate" name="becomeUninfectiousRate" lower="0.0" upper="Infinity" value="1.0"/>
        <parameter spec="parameter.RealParameter" id="samplingProportion" name="samplingProportion" lower="0.0" upper="1.0" value="0.01"/>
    </BirthDeathSkylineModel>
    <branchRateModel spec="beast.evolution.branchratemodel.NonHomogeneousClockModel" id="RelaxedClock" clock.rate="@ucldMean" tree="@tree" scaleFactor="@nonhomogeneousClockScaleFactor" growthFactor="@nonhomogeneousClockGrowthFactor" middle="@nonhomogeneousClockMiddle">
        <LogNormal id="LogNormalDistributionModel" S="@ucldStdevParameter" meanInRealSpace="true" name="distr">
            <parameter spec="parameter.RealParameter" id="RealParameter.23" estimate="false" lower="0.0" name="M" upper="1.0" value="1.0"/>
        </LogNormal>
    </branchRateModel>
    <!-- The chainLength attribute should be increased to a large number (e.g., 20000000) for non-test runs -->
    <run spec="MCMC" id="mcmc" chainLength="100000">
        <state spec="State" id="state" storeEvery="5000">
            <input name="stateNode" idref="tree"/>
            <parameter spec="parameter.RealParameter" id="ucldMean" name="stateNode" value="1.0"/>
            <parameter spec="parameter.RealParameter" id="ucldStdevParameter" lower="0.0" name="stateNode" estimate="false" value="0.000001"/>
            <parameter spec="parameter.RealParameter" id="nonhomogeneousClockScaleFactor" name="stateNode" lower="0.0" upper="10.0" value="1.0"/>
            <parameter spec="parameter.RealParameter" id="nonhomogeneousClockGrowthFactor" name="stateNode" value="500.0"/>
            <parameter spec="parameter.RealParameter" id="nonhomogeneousClockMiddle" name="stateNode" value="600.0"/>
            <!-- Start intrinsic parameters -->
            <!-- End intrinsic parameters -->
            <!-- Start transcriptional parameters -->
            <!-- End transcriptional parameters -->
            <!-- We include a "default" rate fixed at 1 that corresponds to (unlikely) transitions with no transcriptional explanation.
            All other rates in the substitution matrices will be estimated relative to this.
            If no other transcriptional rate parameters are specified, then the substitution matrices will correspond to those of the Lewis Mk model. -->
            <parameter spec="parameter.RealParameter" id="default_rate" name="stateNode" estimate="false" value="1.0"/>
        </state>
        <init spec="RandomTree" id="RandomTree.t:alignment" estimate="false" initial="@tree" taxa="@alignment">
            <populationModel spec="ConstantPopulation" id="ConstantPopulation0.t:alignment">
                <parameter spec="parameter.RealParameter" id="randomPopSize.t:alignment" name="popSize" value="1.0"/>
            </populationModel>
        </init>
        <distribution spec="CompoundDistribution" id="posterior">
            <distribution spec="CompoundDistribution" id="prior">
                <distribution spec="bdsky.evolution.speciation.BirthDeathSkylineModel" id="birthDeath" becomeUninfectiousRate="@becomeUninfectiousRate" reproductiveNumber="@reproductiveNumber" samplingProportion="@samplingProportion" tree="@tree">
                    <parameter spec="parameter.RealParameter" id="origin_birthDeath" estimate="false" lower="1250.0" name="origin" upper="1250.0" value="1250.0"/>
                </distribution>
                <prior id="becomeUninfectiousRatePrior_birthDeath" name="distribution" x="@becomeUninfectiousRate">
                    <LogNormal id="LogNormalDistributionModel.1" name="distr">
                        <parameter spec="parameter.RealParameter" id="RealParameter.13" estimate="false" name="M" value="0.0"/>
                        <parameter spec="parameter.RealParameter" id="RealParameter.14" estimate="false" name="S" value="1.0"/>
                    </LogNormal>
                </prior>
                <prior id="reproductiveNumberPrior_birthDeath" name="distribution" x="@reproductiveNumber">
                    <LogNormal id="LogNormalDistributionModel.2" name="distr">
                        <parameter spec="parameter.RealParameter" id="RealParameter.15" estimate="false" name="M" value="0.0"/>
                        <parameter spec="parameter.RealParameter" id="RealParameter.16" estimate="false" name="S" value="1.0"/>
                    </LogNormal>
                </prior>
                <prior id="samplingProportionPrior_birthDeath" name="distribution" x="@samplingProportion">
                    <Beta id="Beta.1" name="distr">
                        <parameter spec="parameter.RealParameter" id="RealParameter.17" estimate="false" name="alpha" value="1.0"/>
                        <parameter spec="parameter.RealParameter" id="RealParameter.18" estimate="false" name="beta" value="1.0"/>
                    </Beta>
                </prior>
                <prior id="MeanRatePrior" name="distribution" x="@ucldMean">
                    <Uniform id="Uniform.4" name="distr" upper="Infinity"/>
                </prior>
                <prior id="nonhomogeneousClockScaleFactorPrior" name="distribution" x="@nonhomogeneousClockScaleFactor">
                    <Exponential id="nonhomogeneousClockScaleFactorPriorDistribution" name="distr">
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockScaleFactorPriorDistributionMean" estimate="false" name="mean">1.0</parameter>
                    </Exponential>
                </prior>
                <prior id="nonhomogeneousClockGrowthFactorPrior" name="distribution" x="@nonhomogeneousClockGrowthFactor">
                    <Normal id="nonhomogeneousClockGrowthFactorPriorDistribution" name="distr">
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockGrowthFactorPriorDistributionMean" estimate="false" name="mean" value="500.0"/>
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockGrowthFactorPriorDistributionSigma" estimate="false" name="sigma" value="500.0"/>
                    </Normal>
                </prior>
                <prior id="nonhomogeneousClockMiddlePrior" name="distribution" x="@nonhomogeneousClockMiddle">
                    <Normal id="nonhomogeneousClockMiddlePriorDistribution" name="distr">
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockMiddlePriorDistributionMean" estimate="false" name="mean" value="500.0"/>
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockMiddlePriorDistributionSigma" estimate="false" name="sigma" value="500.0"/>
                    </Normal>
                </prior>
            </distribution>
            <distribution spec="CompoundDistribution" id="likelihood" useThreads="true">
                <!-- Start character distributions -->
                <!-- End character distributions -->
            </distribution>
        </distribution>
        <operator spec="ScaleOperator" id="BDSKY_SerialTreeScaler.t:alignment" scaleFactor="0.5" tree="@tree" weight="3.0"/>
        <operator spec="ScaleOperator" id="BDSKY_SerialTreeRootScaler.t:alignment" rootOnly="true" scaleFactor="0.5" tree="@tree" weight="3.0"/>
        <operator spec="Uniform" id="BDSKY_SerialUniformOperator.t:alignment" tree="@tree" weight="30.0"/>
        <operator spec="SubtreeSlide" id="BDSKY_SerialSubtreeSlide.t:alignment" tree="@tree" weight="15.0"/>
        <operator spec="Exchange" id="BDSKY_SerialNarrow.t:alignment" tree="@tree" weight="0.0"/>
        <operator spec="Exchange" id="BDSKY_SerialWide.t:alignment" isNarrow="false" tree="@tree" weight="3.0"/>
        <operator spec="WilsonBalding" id="BDSKY_SerialWilsonBalding.t:alignment" tree="@tree" weight="3.0"/>
        <operator spec="ScaleOperator" id="becomeUninfectiousRateScaler" parameter="@becomeUninfectiousRate" weight="2.0"/>
        <operator spec="ScaleOperator" id="reproductiveNumberScaler" parameter="@reproductiveNumber" weight="10.0"/>
        <operator spec="ScaleOperator" id="samplingProportionScaler" parameter="@samplingProportion" weight="10.0"/>
        <operator spec="UpDownOperator" id="updownBD" scaleFactor="0.75" weight="2.0">
            <up idref="reproductiveNumber"/>
            <down idref="becomeUninfectiousRate"/>
        </operator>
        <operator spec="ScaleOperator" id="ucldMeanScaler" parameter="@ucldMean" scaleFactor="0.5" weight="1.0"/>
        <operator spec="UpDownOperator" id="relaxedUpDownOperator" scaleFactor="0.75" weight="3.0">
            <up idref="ucldMean"/>
            <down idref="Tree.t:alignment"/>
        </operator>
        <operator spec="ScaleOperator" id="nonhomogeneousClockScaleFactorOperator" parameter="@nonhomogeneousClockScaleFactor" weight="1.0"/>
        <operator spec="ScaleOperator" id="nonhomogeneousClockGrowthFactorOperator" parameter="@nonhomogeneousClockGrowthFactor" weight="1.0"/>
        <operator spec="ScaleOperator" id="nonhomogeneousClockMiddleOperator" parameter="@nonhomogeneousClockMiddle" weight="1.0"/>
        <!-- Start transcriptional operators -->
        <!-- End transcriptional operators -->
        <logger spec="Logger" id="tracelog" fileName="beast.log" logEvery="1000" model="@posterior" sanitiseHeaders="true" sort="smart">
            <log idref="posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
            <log spec="beast.base.evolution.tree.TreeHeightLogger" id="TreeHeight.t:alignment" tree="@tree"/>
            <log idref="birthDeath"/>
            <log idref="becomeUninfectiousRate"/>
            <log idref="reproductiveNumber"/>
            <log idref="samplingProportion"/>
            <log idref="ucldMean"/>
            <log idref="ucldStdevParameter"/>
            <log spec="beast.evolution.branchratemodel.RateStatistic" id="rate" branchratemodel="@RelaxedClock" tree="@tree"/>
            <log idref="nonhomogeneousClockScaleFactor"/>
            <log idref="nonhomogeneousClockGrowthFactor"/>
            <log idref="nonhomogeneousClockMiddle"/>
            <!-- Start transcriptional loggers -->
            <!-- End transcriptional loggers -->
        </logger>
        <logger spec="Logger" id="screenlog" logEvery="1000">
            <log idref="posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
        </logger>
        <logger spec="Logger" id="treelog.t:alignment" fileName="$(tree).trees" logEvery="1000" mode="tree">
            <log spec="beast.base.evolution.tree.TreeWithMetaDataLogger" id="TreeWithMetaDataLogger.t:alignment" branchratemodel="@RelaxedClock" tree="@tree"/>
        </logger>
        <operatorschedule spec="OperatorSchedule" id="OperatorSchedule"/>
        <logger id="AncestralSequenceLogger" fileName="$(tree).ancestral.trees" logEvery="10000" mode="tree">
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
<parameter spec="parameter.RealParameter" id="{transcriptional_category}_rate" name="stateNode" lower="1.0" upper="Infinity" estimate="{estimate}" value="{value}"/>
"""

"""
BEAST XML distribution template string
"""
distribution_template = """
<distribution spec="TreeLikelihood" id="morphTreeLikelihood.character{vu_ind}" useAmbiguities="true" useTipLikelihoods="true" tree="@tree">
    <data spec="FilteredAlignment" id="filter{vu_ind}" data="@alignment" filter="{vu_ind}">
        <userDataType spec="StandardData" id="morphDataType.character{vu_ind}"/>
    </data>
    <siteModel spec="SiteModel" id="morphSiteModel.character{vu_ind}">
        <parameter spec="parameter.RealParameter" id="mutationRate.character{vu_ind}" estimate="false" name="mutationRate" value="1.0"/>
        <parameter spec="parameter.RealParameter" id="gammaShape.character{vu_ind}" estimate="false" name="shape" value="1.0"/>
        <substModel spec="GeneralSubstitutionModel" id="SubstModel.character{vu_ind}">
            <!-- Equilibrium state frequencies -->
            <frequencies spec="Frequencies" id="equilibriumfreqs.character{vu_ind}" data="@alignment"/>
            <parameter spec="parameter.CompoundValuable" id="rates.character{vu_ind}" name="rates">
                <!-- Start rate vars -->
                <!-- End rate vars -->
            </parameter>
        </substModel>
    </siteModel>
    <rootFrequencies spec="Frequencies" id="rootfreqs.character{vu_ind}">
        <!-- Start root frequencies -->
        <!-- End root frequencies -->
    </rootFrequencies>
    <branchRateModel idref="RelaxedClock"/>
</distribution>
"""

"""
BEAST XML single rate variable template
"""
single_var_template = """
<var idref="{transcriptional_category}_rate"/>
"""

"""
BEAST XML multiple rate variable template (rate parameters being added should be appended as child var elements)
"""
multiple_var_template = """
<var spec="beast.core.util.Sum"/>
"""

"""
BEAST XML frequencies template
"""
frequencies_template = """
<frequencies spec="parameter.RealParameter" id="rootfrequencies.character{vu_ind}" value="{frequencies}" estimate="false"/>
"""

"""
BEAST XML operator template for rate variables
"""
transcriptional_rate_parameter_operator_template = """
<operator id="Scaler.{transcriptional_category}_rate" spec="ScaleOperator" scaleFactor="0.5" weight="1" parameter="@{transcriptional_category}_rate"/>
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
<log spec="beast.evolution.likelihood.AncestralSequenceLogger" id="morphTreeLikelihood.character{vu_ind}.anclogger" data="@filter{vu_ind}" siteModel="@morphSiteModel.character{vu_ind}" branchRateModel="@RelaxedClock" tree="@tree" tag="morphTreeLikelihood.character{vu_ind}" useAmbiguities="true" useTipLikelihoods="true" ascii="false"/>
"""
