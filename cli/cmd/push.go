package cmd

import (
	"bytes"
	"encoding/json"
	"fmt"
	"github.com/spf13/cobra"
	"io"
	"io/ioutil"
	"mime/multipart"
	"net/http"
	"os"
	"path"
)

// pushCmd represents the push command
var pushCmd = &cobra.Command{
	Use:   "push",
	Short: "A brief description of your command",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		if len(args) == 0 {
			_, err := fmt.Fprintf(cmd.ErrOrStderr(), "you need to specify the directory containing the notebook that you want to push ")
			return err
		}

		return pushNotebook(args[0])
	},
}

func init() {
	rootCmd.AddCommand(pushCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// pushCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// pushCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}

type NotebookMetadata struct {
	Name      string `json:"name"`
	Filename  string `json:"kernel"`
	RemoteURL string `json:"remote"`
}

func pushNotebook(dir string) error {
	f, err := ioutil.ReadFile(path.Join(dir, "kernel-metadata.json"))
	if err != nil {
		return err
	}

	metadata := NotebookMetadata{}
	err = json.Unmarshal(f, &metadata)
	if err != nil {
		return err
	}

	req, err := makePushRequest(
		metadata.Name,
		path.Join(dir, metadata.Filename),
		metadata.RemoteURL+"/push", // TODO: handle RemoteURL ending with '/'
	)
	if err != nil {
		return err
	}

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
		return err
	}

	body, err := ioutil.ReadAll(res.Body)
	if err != nil {
		return err
	}
	fmt.Println(string(body))

	return nil
}

func makePushRequest(notebookName, notebookPath, url string) (*http.Request, error) {
	buf := new(bytes.Buffer)
	w := multipart.NewWriter(buf)

	file, err := w.CreateFormFile("file", path.Base(notebookPath))
	if err != nil {
		return nil, err
	}

	notebook, err := os.Open(notebookPath)
	if err != nil {
		return nil, err
	}
	defer notebook.Close()

	_, err = io.Copy(file, notebook)
	if err != nil {
		return nil, err
	}
	w.Close()

	req, err := http.NewRequest(
		"POST",
		fmt.Sprintf("%s?name=%s", url, notebookName),
		buf,
	)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Content-Type", w.FormDataContentType())

	return req, nil
}
