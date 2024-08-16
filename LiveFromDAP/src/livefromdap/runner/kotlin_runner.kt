import java.io.File
import kotlin.script.experimental.api.*
import kotlin.script.experimental.host.StringScriptSource
import kotlin.script.experimental.jvm.dependenciesFromCurrentContext
import kotlin.script.experimental.jvm.jvm
import kotlin.script.experimental.jvmhost.BasicJvmScriptingHost

object KotlinScriptExecutor {

    private var importFile: String? = null
    private var methodName: String? = null
    private var methodArgs: List<Any>? = null

    fun setImport(importFrom: String) {
        importFile = importFrom
    }

    fun setMethod(importMethod: String, methodArgs: List<Any>) {
        methodName = importMethod
        this.methodArgs = methodArgs
    }

    fun execute() {
        importFile?.let {
            val code = File(it).readText()
            executeScript(code)
            importFile = null
        }

        methodName?.let { name ->
            methodArgs?.let { args ->
                try {
                    val method = eval(name) as? (Array<Any>) -> Any
                    method?.invoke(args.toTypedArray())
                } catch (e: Exception) {
                    println("Method invocation failed: ${e.message}")
                }
            }
            methodName = null
            methodArgs = null
        }
    }

    private fun executeScript(script: String) {
        val compilationConfiguration = ScriptCompilationConfiguration {
            jvm {
                dependenciesFromCurrentContext(wholeClasspath = true)
            }
        }

        val evaluationConfiguration = ScriptEvaluationConfiguration {
            jvm {
                baseClassLoader(null)
            }
        }

        val scriptingHost = BasicJvmScriptingHost()
        val scriptSource = StringScriptSource(script)

        val compilationResult = scriptingHost.compiler(scriptSource, compilationConfiguration)

        if (compilationResult is ResultWithDiagnostics.Success) {
            val evaluationResult = scriptingHost.evaluator(compilationResult.value, evaluationConfiguration)
            if (evaluationResult is ResultWithDiagnostics.Failure) {
                println("Evaluation failed:\n${evaluationResult.reports.joinToString("\n") { it.message }}")
            }
        } else {
            println("Compilation failed:\n${compilationResult.reports.joinToString("\n") { it.message }}")
        }
    }

    private fun eval(code: String): Any? {
        return try {
            val script = "val result = $code\nresult"
            executeScript(script)
        } catch (e: Exception) {
            println("Evaluation error: ${e.message}")
            null
        }
    }
}

fun main() {
    while(true){
        
    }
}
